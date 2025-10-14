library(shiny)
library(readxl)
library(ggplot2)
library(dplyr)

# Função genérica para criação de gráficos
criar_grafico <- function(dados, titulo) {
  ggplot(dados, aes(x = reorder(Categoria, Valor), y = Valor, fill = Categoria)) +
    geom_col(show.legend = FALSE) +
    coord_flip() +
    labs(title = titulo, x = "", y = "Percentual") +
    theme_minimal(base_size = 14)
}

# Interface ---------------------------------------------------------
ui <- fluidPage(
  titlePanel("Painel de Acompanhamento dos Editais"),
  
  sidebarLayout(
    sidebarPanel(
      h4("Navegação"),
      selectInput(
        "edital", "Selecione o Edital:",
        choices = c("Edital 40", "Edital 43")
      ),
      selectInput(
        "secao", "Selecione a Seção:",
        choices = c("Visão geral", "Gráficos comparativos", "Gráficos por município/disciplina")
      ),
      width = 3
    ),
    
    mainPanel(
      # Abas superiores sincronizadas com o menu lateral
      tabsetPanel(
        id = "abas",
        tabPanel("Visão geral", uiOutput("aba_visao_geral")),
        tabPanel("Gráficos comparativos", uiOutput("aba_graficos_comparativos")),
        tabPanel("Gráficos por município/disciplina", uiOutput("aba_graficos_municipio"))
      )
    )
  )
)

# Servidor ---------------------------------------------------------
server <- function(input, output, session) {
  
  # Bases organizadas por edital
  bases <- reactive({
    list(
      "Edital 40" = list(
        "Vitória 40" = read_excel("vitoria_40.xlsx"),
        "Serra 40"   = read_excel("serra_40.xlsx"),
        "Fundão 40"  = read_excel("fundao_40.xlsx"),
        "Santa Teresa 40" = read_excel("santa_teresa_40.xlsx")
      ),
      "Edital 43" = list(
        "Vitória 43" = read_excel("vitoria_43.xlsx"),
        "Serra 43"   = read_excel("serra_43.xlsx"),
        "Fundão 43"  = read_excel("fundao_43.xlsx"),
        "Santa Teresa 43" = read_excel("santa_teresa_43.xlsx")
      )
    )
  })
  
  # 🔁 Sincroniza menu lateral e abas
  observeEvent(input$secao, {
    updateTabsetPanel(session, "abas", selected = input$secao)
  })
  observeEvent(input$abas, {
    updateSelectInput(session, "secao", selected = input$abas)
  })
  
  # =================== ABA 1 - VISÃO GERAL =======================
  output$aba_visao_geral <- renderUI({
    edital <- input$edital
    dados_edital <- bases()[[edital]]
    
    if (is.null(dados_edital)) return(h4("Carregando dados..."))
    
    tagList(
      h3(paste("Visão Geral -", edital)),
      lapply(names(dados_edital), function(nome) {
        plotOutput(outputId = paste0("grafico_visao_", gsub(" ", "_", nome)))
      })
    )
  })
  
  # Renderiza gráficos da aba “Visão Geral”
  observe({
    edital <- input$edital
    dados_edital <- bases()[[edital]]
    if (is.null(dados_edital)) return(NULL)
    
    lapply(names(dados_edital), function(nome) {
      local({
        nm <- nome
        output[[paste0("grafico_visao_", gsub(" ", "_", nm))]] <- renderPlot({
          criar_grafico(dados_edital[[nm]], paste("Resumo geral de", nm))
        })
      })
    })
  })
  
  # =================== ABA 2 - GRÁFICOS COMPARATIVOS =======================
  output$aba_graficos_comparativos <- renderUI({
    edital <- input$edital
    dados_edital <- bases()[[edital]]
    if (is.null(dados_edital)) return(NULL)
    
    tagList(
      h3(paste("Gráficos Comparativos -", edital)),
      plotOutput("grafico_comparativo")
    )
  })
  
  output$grafico_comparativo <- renderPlot({
    edital <- input$edital
    dados_edital <- bases()[[edital]]
    if (is.null(dados_edital)) return(NULL)
    
    # Exemplo: comparação de médias de cada município
    resumo <- do.call(rbind, lapply(names(dados_edital), function(nome) {
      data.frame(
        Municipio = nome,
        Media = mean(dados_edital[[nome]]$Valor, na.rm = TRUE)
      )
    }))
    
    ggplot(resumo, aes(x = Municipio, y = Media, fill = Municipio)) +
      geom_col(show.legend = FALSE) +
      labs(title = paste("Comparativo geral entre municípios -", edital),
           x = "", y = "Média (%)") +
      theme_minimal(base_size = 14)
  })
  
  # =================== ABA 3 - MUNICÍPIO / DISCIPLINA =======================
  output$aba_graficos_municipio <- renderUI({
    edital <- input$edital
    dados_edital <- bases()[[edital]]
    if (is.null(dados_edital)) return(NULL)
    
    tagList(
      h3(paste("Gráficos por Município e Disciplina -", edital)),
      lapply(names(dados_edital), function(nome) {
        plotOutput(outputId = paste0("grafico_disc_", gsub(" ", "_", nome)))
      })
    )
  })
  
  observe({
    edital <- input$edital
    dados_edital <- bases()[[edital]]
    if (is.null(dados_edital)) return(NULL)
    
    lapply(names(dados_edital), function(nome) {
      local({
        nm <- nome
        output[[paste0("grafico_disc_", gsub(" ", "_", nm))]] <- renderPlot({
          criar_grafico(dados_edital[[nm]], paste("Município e Disciplinas -", nm))
        })
      })
    })
  })
}

# Executa o app
shinyApp(ui, server)
