import streamlit as st
import plotly.express as px
import pandas as pd


# ------------------------------------------------------------
# CONFIGURAÇÕES GERAIS DO APP
# ------------------------------------------------------------
st.set_page_config(page_title="Painel de Análise dos Editais", layout="wide")

st.title("📊 Painel de Acompanhamento dos Editais por Município")

# ------------------------------------------------------------
# FUNÇÃO PARA LER E UNIFICAR AS ABAS VÁLIDAS
# ------------------------------------------------------------
def carregar_dados(caminho_arquivo):
    abas_excluir = ["AUX", "INDICE", "Log", "CHAMADA", "Configuração de Email"]
    xls = pd.ExcelFile(caminho_arquivo)
    dados = []
    for aba in xls.sheet_names:
        if aba not in abas_excluir:
            df = pd.read_excel(xls, aba)
            dados.append(df)
    if dados:
        df_final = pd.concat(dados, ignore_index=True)
        return df_final
    else:
        return pd.DataFrame()

# ------------------------------------------------------------
# UPLOAD DOS ARQUIVOS (UM PARA CADA MUNICÍPIO)
# ------------------------------------------------------------
st.sidebar.header("📂 Envie os arquivos Excel")
st.sidebar.markdown("Cada arquivo deve conter as disciplinas de um município.")

municipios = ["Vitória", "Serra", "Santa Teresa", "Fundão"]

arquivos = {}
for m in municipios:
    arquivos[m] = st.sidebar.file_uploader(f"Arquivo de {m}", type=["xlsx"], key=m)

# ------------------------------------------------------------
# LEITURA DOS ARQUIVOS
# ------------------------------------------------------------
dados_municipios = {}
for m in municipios:
    if arquivos[m]:
        df = carregar_dados(arquivos[m])
        df["Município"] = m
        dados_municipios[m] = df

# ------------------------------------------------------------
# ABAS PRINCIPAIS DO DASHBOARD
# ------------------------------------------------------------
aba1, aba2, aba3 = st.tabs([
    "📊 Visão Geral",
    "🏙️ Comparativo entre Municípios",
    "🥧 Gráficos de Pizza por Disciplina"
])

# ------------------------------------------------------------
# ABA 1 - VISÃO GERAL
# ------------------------------------------------------------
with aba1:
    st.header("📊 Visão Geral dos Indicadores")
    st.write(
        "Nesta aba, você visualiza o total dos principais indicadores de **cada município**, "
        "mostrados individualmente em gráficos de barras."
    )
    
    # Lista das colunas de interesse
    colunas_interesse = [
        "Total de candidatos",
        "Aguardando análise",
        "Eliminados",
        "Reclassificados",
        "Contratados",
        "Documentos analisados",
        "Convocados"
    ]
    # Cria um gráfico separado para cada município
    for municipio, df_mun in dados_municipios.items():
        if not df_mun.empty:
            st.subheader(f"🏙️ {municipio}")
            
            # Soma apenas dentro do próprio município
            soma_municipio = df_mun[colunas_interesse].sum().reset_index()
            soma_municipio.columns = ["Indicador", "Quantidade"]
                     
            # Cria o gráfico de barras
            fig = px.bar(
                soma_municipio,
                x="Indicador",
                y="Quantidade",
                text="Quantidade",
                title=f"Indicadores gerais - {municipio}",
                color="Indicador"
            )
            fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            fig.update_layout(
                showlegend=False,
                yaxis_title="Quantidade",
                xaxis_title=None,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")
# ------------------------------------------------------------
# ABA 2 - GRÁFICOS DE BARRAS COMPARATIVOS ENTRE MUNICÍPIOS
# ------------------------------------------------------------
with aba2:
    st.header("🏙️ Gráficos Comparativos entre Municípios")
    st.write("Comparação entre indicadores de diferentes municípios.")

    indicadores = ["Convocados", "Eliminados", "Reclassificados", "Documentos analisados"]
    for indicador in indicadores:
        fig_bar = px.bar(
            df,
            x="Município",
            y=indicador,
            color="Município",
            title=f"{indicador} por Município"
        )
        st.plotly_chart(fig_bar, use_container_width=True)


# ------------------------------------------------------------
# ABA 3 - GRÁFICOS DE PIZZA POR MUNICÍPIO E DISCIPLINA
# ------------------------------------------------------------
with aba3:
    st.header("🥧 Gráficos de Pizza - Indicadores por Disciplina e Município")
    st.write("Visualização detalhada dos indicadores por disciplina, com totais ao lado dos gráficos.")

    for m, df_municipio in dados_municipios.items():
        if not df_municipio.empty:
            st.subheader(f"🏫 {m}")

            for _, linha in df_municipio.iterrows():
                disciplina = linha["Disciplina"]

                # Retira "Documentos analisados" da pizza
                valores_pizza = linha[["Aguardando análise", "Contratados","Eliminados", "Reclassificados"]]

                # Cria o gráfico de pizza
                fig_pizza = px.pie(
                    values=valores_pizza.values,
                    names=valores_pizza.index,
                    title=f"{disciplina} - {m}"
                )

                # Mostra gráfico e totais lado a lado
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.plotly_chart(fig_pizza, use_container_width=True)

                with col2:
                    st.markdown(f"""
                    **📘 Disciplina:** {disciplina}  
                    **👥 Total de candidatos:** {linha['Total de candidatos']}  
                    **📄 Documentos analisados:** {linha['Documentos analisados']}  
                    **✅ Convocados:** {linha['Convocados']}
                    """)
