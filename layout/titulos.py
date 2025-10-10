import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# ===========================
# CONFIGURAÇÕES INICIAIS
# ===========================
st.set_page_config(
    page_title="Painel de Contratação - Municípios",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏙️ Painel Interativo de Contratação por Município")
st.markdown(
    """
    Este painel apresenta dados consolidados dos processos de contratação de diferentes municípios,
    permitindo comparações entre disciplinas e indicadores.
    """
)

# ===========================
# FUNÇÃO PARA CARREGAR PLANILHAS
# ===========================
@st.cache_data
def carregar_planilhas(municipio, arquivo):
    # Abas que devem ser ignoradas
    abas_excluir = ["AUX", "INDICE", "LOG", "CHAMADA", "Configuração de Email"]

    xls = pd.ExcelFile(arquivo)
    dados_municipio = []

    for aba in xls.sheet_names:
        if aba.upper() not in [a.upper() for a in abas_excluir]:
            df = pd.read_excel(xls, sheet_name=aba)
            df["Disciplina"] = aba
            df["Município"] = municipio
            dados_municipio.append(df)

    if dados_municipio:
        df_municipio = pd.concat(dados_municipio, ignore_index=True)
        # Excluir colunas desnecessárias, se existirem
        colunas_excluir = ["Ampla Concorrência", "Negros", "Deficientes", "Indígenas"]
        df_municipio = df_municipio.drop(columns=[c for c in colunas_excluir if c in df_municipio.columns], errors="ignore")
        return df_municipio
    else:
        return pd.DataFrame()

# ===========================
# UPLOAD DOS ARQUIVOS (4 MUNICÍPIOS)
# ===========================
st.sidebar.header("📂 Carregue os arquivos de cada município")

arquivos = {}
municipios = ["Vitória", "Serra", "Santa Teresa", "Fundão"]

for municipio in municipios:
    arquivos[municipio] = st.sidebar.file_uploader(f"📘 {municipio}", type=["xlsx"])

# ===========================
# PROCESSAR DADOS
# ===========================
dfs = []
for municipio, arquivo in arquivos.items():
    if arquivo is not None:
        df_mun = carregar_planilhas(municipio, arquivo)
        if not df_mun.empty:
            dfs.append(df_mun)

if dfs:
    df_total = pd.concat(dfs, ignore_index=True)
    st.success("✅ Dados carregados com sucesso para os municípios selecionados.")
else:
    st.warning("Envie ao menos um arquivo Excel para começar a análise.")
    st.stop()

# ===========================
# ABA 1 - VISÃO GERAL
# ===========================
aba1, aba2 = st.tabs(["📈 Visão Comparativa", "🥧 Gráficos por Disciplina"])

# ---------------------------
# ABA 1: GRÁFICO DE BARRAS COMPARATIVO
# ---------------------------
with aba1:
    st.subheader("📊 Comparativo entre Municípios por Disciplina")

    # Verifica se existe a coluna "Total de Candidatos" ou similar
    colunas_qtd = [c for c in df_total.columns if "Total" in c or "total" in c or "Quantidade" in c]

    if colunas_qtd:


