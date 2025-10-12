# ------------------------------------------------------------
# APP STREAMLIT - INDICADORES POR MUNICÍPIO E DISCIPLINA
# ------------------------------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ------------------------------------------------------------
# CONFIGURAÇÕES INICIAIS
# ------------------------------------------------------------
st.set_page_config(page_title="Indicadores - Editais 40 e 42/2024", layout="wide")

st.title("📊 Indicadores dos Editais 40/2024 e 42/2024")
st.markdown("Análise comparativa por **município** e **disciplina**, com base nos indicadores dos processos seletivos.")
st.markdown("**OBSERVAÇÃO**: NO MOMENTO A BASE DE DADOS É A MESMA NOS 2 (DOIS) EDITAIS E NOS 4 (QUATRO MUNICÍPIOS) ENQUANTO ESTAMOS CONSTRUINDO A ESTRUTURA DO MVP.")

# ------------------------------------------------------------
# FUNÇÃO PARA CARREGAR OS DADOS
# ------------------------------------------------------------
def carregar_dados():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    arquivos = {
        "Vitória 40": os.path.join(BASE_DIR, "vitoria_40.xlsx"),
        "Serra 40": os.path.join(BASE_DIR, "serra_40.xlsx"),
        "Fundão 40": os.path.join(BASE_DIR, "fundao_40.xlsx"),
        "Santa Teresa 40": os.path.join(BASE_DIR, "santa_teresa_40.xlsx"),
        "Vitória 42": os.path.join(BASE_DIR, "vitoria_42.xlsx"),
        "Serra 42": os.path.join(BASE_DIR, "serra_42.xlsx"),
        "Fundão 42": os.path.join(BASE_DIR, "fundao_42.xlsx"),
        "Santa Teresa 42": os.path.join(BASE_DIR, "santa_teresa_42.xlsx"),
    }

    dados = {}
    for nome, caminho in arquivos.items():
        if os.path.exists(caminho):
            dados[nome] = pd.read_excel(caminho)
        else:
            print(f"⚠️ Arquivo não encontrado: {caminho}")
    return dados


# ------------------------------------------------------------
# CARREGAMENTO DOS DADOS
# ------------------------------------------------------------
dados_municipios = carregar_dados()

# ------------------------------------------------------------
# MENU LATERAL
# ------------------------------------------------------------
st.sidebar.title("📁 Menu de Navegação")
pagina = st.sidebar.radio(
    "Selecione a página:",
    ("Página Inicial", "Edital 40/2024", "Edital 42/2024")
)

# ------------------------------------------------------------
# PÁGINA INICIAL
# ------------------------------------------------------------
if pagina == "Página Inicial":
    st.header("🏠 Página Inicial")
    st.markdown("""
    Este painel apresenta os **indicadores dos editais 40/2024 e 42/2024**,
    organizados por **município** e **disciplina**.  
    Utilize o menu lateral para navegar entre os editais e visualizar os gráficos.
    """)

# ------------------------------------------------------------
# FUNÇÃO PARA EXIBIR OS DADOS DE UM EDITAL
# ------------------------------------------------------------
def exibir_edital(edital_numero):
    st.header(f"📘 Indicadores - Edital {edital_numero}/2024")
    st.markdown(f"Análise dos indicadores do **Edital {edital_numero}/2024**, por município e disciplina.")

    # Selecionar os dados do edital
    dados_edital = {k: v for k, v in dados_municipios.items() if k.endswith(str(edital_numero))}

    if not dados_edital:
        st.warning("⚠️ Nenhum dado carregado. Verifique os arquivos Excel.")
        return

    # Verificar se algum arquivo está faltando
    municipios_faltando = [m for m in ["Vitória", "Serra", "Fundão", "Santa Teresa"] if f"{m} {edital_numero}" not in dados_edital]
    if municipios_faltando:
        st.error(f"🚨 Alguns arquivos de dados não foram encontrados: {', '.join(municipios_faltando)}")
        return

    # Criar abas
    aba_geral, aba_barras, aba_pizza = st.tabs(["📋 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos de Pizza"])

    # ------------------------------------------------------------
    # ABA 1: VISÃO GERAL
    # ------------------------------------------------------------
    with aba_geral:
            # Somatório por município
        st.subheader("📈 Somatório dos Indicadores por Município")
        indicadores = [
             "Aguardando análise", "Reclassificados", "Eliminados", "Contratados"
        ]

        resumo = []
        for municipio, df in dados_edital.items():
            soma = df[indicadores].sum(numeric_only=True)
            soma["Município"] = municipio
            resumo.append(soma)

        df_resumo = pd.DataFrame(resumo)
        fig_bar = px.bar(
            df_resumo.melt(id_vars="Município", var_name="Indicador", value_name="Total"),
            x="Município", y="Total", color="Indicador",
            title=f"Comparativo de Indicadores - Edital {edital_numero}/2024"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # -------------------------------
        # 📊 Selecionar município
        # -------------------------------
        st.subheader("📋 Tabela Descritiva por Município")

        municipios_disponiveis = list(dados_edital.keys())
        municipio_escolhido = st.selectbox("Selecione o município:", municipios_disponiveis)

        if municipio_escolhido:
            df = dados_edital[municipio_escolhido]
            st.markdown(f"### 📍 {municipio_escolhido}")
            st.dataframe(df.describe(include='all'))

        # -------------------------------
        # 🔍 Visualização dos dados brutos
        # -------------------------------
        with st.expander("📄 Ver dados completos do município selecionado"):
            st.dataframe(df)


    # ------------------------------------------------------------
    # ABA 2: GRÁFICOS COMPARATIVOS ENTRE AS DISCIPLINAS 
    # ------------------------------------------------------------
    with aba_barras:
        st.subheader("📊 Comparativo de Indicadores Entre as Disciplinas do Município")
    
        if not dados_edital:
            st.warning("⚠️ Nenhum dado carregado para gerar os gráficos.")
        else:
            municipios_disponiveis = list(dados_edital.keys())
            municipio_escolhido = st.selectbox("Selecione o município para visualizar:", municipios_disponiveis)
    
            if municipio_escolhido:
                df = dados_edital[municipio_escolhido]
    
                try:
                    fig = px.bar(
                        df,
                        x="Disciplina",
                        y=["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Contratados"],
                        barmode="group",
                        title=f"{municipio_escolhido} - Edital {edital}/2024"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao gerar gráfico para {municipio_escolhido}: {e}")

    # ------------------------------------------------------------
    # ABA 3: GRÁFICOS DE PIZZA
    # ------------------------------------------------------------
    with aba_pizza:
        st.subheader("🥧 Gráficos de Pizza - Indicadores por Disciplina e Município")
        for municipio, df in dados_edital.items():
            if not df.empty:
                st.markdown(f"### {municipio}")
                for _, linha in df.iterrows():
                    disciplina = linha["Disciplina"]
                    valores = linha[["Aguardando análise", "Eliminados", "Reclassificados","Contratados"]]  # sem "Documentos analisados"
                    fig_pizza = px.pie(
                        values=valores.values,
                        names=valores.index,
                        title=f"{disciplina} - {municipio}"
                    )
                    total = linha["Total de candidatos"]
                    documentos = linha["Documentos analisados"]
                    convocados = linha["Convocados"]

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.plotly_chart(fig_pizza, use_container_width=True)
                    with col2:
                        st.markdown(f"**Total de candidatos:** {total}")
                        st.markdown(f"**Documentos analisados:** {documentos}")
                        st.markdown(f"**Convocados:** {convocados}")

# ------------------------------------------------------------
# CHAMADA DE CADA EDITAL
# ------------------------------------------------------------
if pagina == "Edital 40/2024":
    exibir_edital(40)
elif pagina == "Edital 42/2024":
    exibir_edital(42)
