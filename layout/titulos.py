import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# =========================
# Configuração da página
# =========================
st.set_page_config(
    page_title="Indicadores Educacionais",
    layout="wide",
    page_icon="📘"
)

# =========================
# Função para carregar dados
# =========================
@st.cache_data
def carregar_dados(arquivo):
    try:
        return pd.read_excel(arquivo)
    except Exception as e:
        st.error(f"Erro ao carregar {arquivo}: {e}")
        return pd.DataFrame()

# =========================
# Mapeamento dos arquivos
# =========================
bases = {
    "Vitória 40": "vitoria_40.xlsx",
    "Serra 40": "serra_40.xlsx",
    "Fundão 40": "fundao_40.xlsx",
    "Santa Teresa 40": "santa_teresa_40.xlsx",
    "Vitória 43": "vitoria_43.xlsx",
    "Serra 43": "serra_43.xlsx",
    "Fundão 43": "fundao_43.xlsx",
    "Santa Teresa 43": "santa_teresa_43.xlsx"
}

# =========================
# Layout principal
# =========================
st.title("📘 Indicadores Educacionais - Editais 40 e 43/2024")
st.write("Análise dos indicadores educacionais por município e disciplina.")

# =========================
# Menu lateral
# =========================
with st.sidebar:
    st.subheader("📂 Seções do Relatório")
    edital = st.selectbox("Selecione o Edital", ["Edital 40/2024", "Edital 43/2024"])

    menu_selecionado = option_menu(
        menu_title=None,
        options=["Visão Geral", "Gráficos Comparativos", "Gráficos Município/Disciplina"],
        icons=["bar-chart", "pie-chart", "activity"],
        default_index=0,
        orientation="vertical"
    )

# =========================
# Criação das abas principais
# =========================
abas = st.tabs(["📊 Visão Geral", "📈 Gráficos Comparativos", "📍 Gráficos Município/Disciplina"])

# Sincroniza a aba ativa com o menu lateral
aba_index = ["Visão Geral", "Gráficos Comparativos", "Gráficos Município/Disciplina"].index(menu_selecionado)

with abas[aba_index]:
    if menu_selecionado == "Visão Geral":
        st.header("📊 Visão Geral dos Indicadores")
        st.write(f"Análise consolidada do {edital}.")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Municípios analisados", len([k for k in bases if edital.split()[1] in k]))
        with col2:
            st.metric("Total de bases disponíveis", len(bases))

        st.info("Esta visão apresenta um resumo geral dos dados por edital.")

    elif menu_selecionado == "Gráficos Comparativos":
        st.header("📈 Gráficos Comparativos")
        st.write(f"Comparação entre os municípios participantes do {edital}.")

        col1, col2 = st.columns(2)
        for i, (nome, arquivo) in enumerate(bases.items()):
            if edital.split()[1] in nome:
                with col1 if i % 2 == 0 else col2:
                    df = carregar_dados(arquivo)
                    if not df.empty:
                        st.bar_chart(df.select_dtypes(include='number'))
                    else:
                        st.warning(f"Sem dados disponíveis para {nome}.")

    elif menu_selecionado == "Gráficos Município/Disciplina":
        st.header("📍 Indicadores por Disciplina e Município")

        municipios_disponiveis = [k for k in bases if edital.split()[1] in k]
        municipio = st.selectbox("Selecione o município", municipios_disponiveis)

        df = carregar_dados(bases[municipio])
        if not df.empty:
            st.write(f"Exibindo dados para **{municipio}**.")
            st.line_chart(df.select_dtypes(include='number'))
        else:
            st.warning(f"Sem dados disponíveis para {municipio}.")

# =========================
# Sincronização automática
# =========================
st.session_state["aba_ativa"] = menu_selecionado
