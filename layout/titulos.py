import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# CONFIGURAÇÕES GERAIS
# ------------------------------------------------------------
st.set_page_config(
    page_title="Painel de Indicadores - Editais 2024",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# MENU LATERAL
# ------------------------------------------------------------
st.sidebar.title("📁 Navegação")
pagina = st.sidebar.radio(
    "Selecione uma opção:",
    ["Página Inicial", "Edital 40/2024", "Edital 42/2024"]
)

# ------------------------------------------------------------
# FUNÇÃO PARA CARREGAR DADOS
# ------------------------------------------------------------
@st.cache_data
def carregar_dados(edital):
    """
    Carrega as bases de dados conforme o edital escolhido.
    Cada edital tem seus próprios arquivos Excel.
    """
    try:
        if edital == "40/2024":
            vitoria = pd.read_excel("vitoria_40.xlsx")
            serra = pd.read_excel("serra_40.xlsx")
            fundao = pd.read_excel("fundao_40.xlsx")
            santa_teresa = pd.read_excel("santa_teresa_40.xlsx")
        elif edital == "42/2024":
            vitoria = pd.read_excel("vitoria_42.xlsx")
            serra = pd.read_excel("serra_42.xlsx")
            fundao = pd.read_excel("fundao_42.xlsx")
            santa_teresa = pd.read_excel("santa_teresa_42.xlsx")
        else:
            return {}

        return {
            "Vitória": vitoria,
            "Serra": serra,
            "Fundão": fundao,
            "Santa Teresa": santa_teresa
        }
    except FileNotFoundError:
        st.error("⚠️ Alguns arquivos de dados não foram encontrados no diretório.")
        return {}

# ------------------------------------------------------------
# PÁGINA INICIAL
# ------------------------------------------------------------
if pagina == "Página Inicial":
    st.title("🏠 Painel de Acompanhamento dos Editais 2024")
    st.markdown("""
    Bem-vindo ao **Painel de Indicadores** dos processos seletivos do Magistério 2024.

    Este painel foi desenvolvido para apresentar informações comparativas entre os 
    **Editais 40/2024** e **42/2024**, com indicadores detalhados por município e por disciplina.

    ---
    **📊 Seções disponíveis:**
    - **Página Inicial**: visão geral e introdução.
    - **Edital 40/2024**: informações, tabelas e gráficos do primeiro edital.
    - **Edital 42/2024**: informações, tabelas e gráficos do segundo edital.

    ---
    Use o menu lateral para navegar.
    """)

# ------------------------------------------------------------
# FUNÇÃO AUXILIAR PARA GRÁFICOS DE BARRAS
# ------------------------------------------------------------
def graficos_indicadores(df, municipio):
    colunas = [
        "Total de candidatos",
        "Aguardando análise",
        "Eliminados",
        "Reclassificados",
        "Contratados",
        "Documentos analisados",
        "Convocados"
    ]
    colunas_presentes = [c for c in colunas if c in df.columns]

    if len(colunas_presentes) > 1:
        df_melt = df.melt(
            id_vars=["Disciplina"] if "Disciplina" in df.columns else None,
            value_vars=colunas_presentes,
            var_name="Indicador",
            value_name="Quantidade"
        )

        fig = px.bar(
            df_melt,
            x="Indicador",
            y="Quantidade",
            color="Indicador",
            title=f"Indicadores Gerais - {municipio}",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------
# TEMPLATE PARA EDITAIS
# ------------------------------------------------------------
def mostrar_edital(edital, titulo):
    st.title(f"📘 Indicadores - Edital {edital}")
    st.markdown(f"Análise dos indicadores do **Edital {edital}**, por município e disciplina.")

    dados_municipios = carregar_dados(edital)

    if not dados_municipios:
        st.warning("⚠️ Nenhum dado carregado. Verifique os arquivos Excel.")
        return

    # Abas internas
    abas = st.tabs(["📋 Visão Geral", "📊 Gráficos Comparativos", "📈 Gráficos por Disciplina"])

    # --------------------------------------------------------
    # ABA 1 - VISÃO GERAL
    # --------------------------------------------------------
    with abas[0]:
        st.subheader("📋 Tabelas Resumidas por Município")
        for municipio, df in dados_municipios.items():
            st.markdown(f"### 🏫 {municipio}")
            st.dataframe(df.head())

    # --------------------------------------------------------
    # ABA 2 - GRÁFICOS COMPARATIVOS
    # --------------------------------------------------------
    with abas[1]:
        st.subheader("📊 Gráficos de Indicadores Gerais")
        for municipio, df in dados_municipios.items():
            st.markdown(f"### 🏙️ {municipio}")
            graficos_indicadores(df, municipio)

    # --------------------------------------------------------
    # ABA 3 - GRÁFICOS POR DISCIPLINA
    # --------------------------------------------------------
    with abas[2]:
        st.subheader("📈 Distribuição por Disciplina")
        for municipio, df in dados_municipios.items():
            st.markdown(f"### 🏫 {municipio}")

            # Gráfico de pizza - Documentos analisados
            if {"Disciplina", "Documentos analisados"}.issubset(df.columns):
                fig_pie = px.pie(
                    df,
                    values="Documentos analisados",
                    names="Disciplina",
                    title=f"Documentos Analisados - {municipio}"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # Gráfico de barras - Convocados x Contratados
            if {"Disciplina", "Convocados", "Contratados"}.issubset(df.columns):
                fig_bar = px.bar(
                    df,
                    x="Disciplina",
                    y=["Convocados", "Contratados"],
                    barmode="group",
                    title=f"Convocados vs Contratados - {municipio}",
                    text_auto=True
                )
                st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------------------------------------
# EXECUÇÃO DAS PÁGINAS DOS EDITAIS
# ------------------------------------------------------------
if pagina == "Edital 40/2024":
    mostrar_edital("40/2024", "Edital 40/2024")

elif pagina == "Edital 42/2024":
    mostrar_edital("42/2024", "Edital 42/2024")
