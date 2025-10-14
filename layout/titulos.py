import streamlit as st
import pandas as pd
import plotly.express as px

# =======================
# CONFIGURAÇÕES INICIAIS
# =======================
st.set_page_config(page_title="Análise dos Editais 40 e 42", layout="wide")

st.sidebar.title("📂 Navegação")
pagina = st.sidebar.radio(
    "Escolha a seção:",
    ["Visão Geral", "Gráficos por Município", "Gráficos Município/Disciplina"]
)

# =======================
# CARREGAMENTO DOS DADOS
# =======================
arquivos = {
    "Vitória 40": "vitoria_40.xlsx",
    "Serra 40": "serra_40.xlsx",
    "Fundão 40": "fundao_40.xlsx",
    "Santa Teresa 40": "santa_teresa_40.xlsx",
    "Vitória 42": "vitoria_42.xlsx",
    "Serra 42": "serra_42.xlsx",
    "Fundão 42": "fundao_42.xlsx",
    "Santa Teresa 42": "santa_teresa_42.xlsx",
}

dados_edital = {}
for nome, caminho in arquivos.items():
    try:
        df = pd.read_excel(f"layout/{caminho}")
        dados_edital[nome] = df
    except Exception as e:
        st.warning(f"Erro ao carregar {caminho}: {e}")

# =======================
# CORES PADRONIZADAS
# =======================
CORES = {
    "Reclassificados": "#1f77b4",       # azul escuro
    "Eliminados": "#aec7e8",            # azul claro
    "Contratados": "#ff7f0e",           # laranja
    "Aguardando análise": "#ffbb78",    # laranja claro
    "Não resposta": "#d62728",          # vermelho
}

# =======================
# PÁGINA

