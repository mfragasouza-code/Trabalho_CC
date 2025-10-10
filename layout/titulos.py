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
        col_qtd = st.selectbox("Selecione a coluna de quantidade:", colunas_qtd)
    else:
        st.error("Não foi possível identificar a coluna de quantidade total.")
        st.stop()

    disciplinas = sorted(df_total["Disciplina"].dropna().unique().tolist())
    disciplina_escolhida = st.selectbox("Escolha uma disciplina:", disciplinas)

    df_disciplina = df_total[df_total["Disciplina"] == disciplina_escolhida]

    fig_barra = px.bar(
        df_disciplina,
        x="Município",
        y=col_qtd,
        color="Município",
        text=col_qtd,
        title=f"Comparativo entre municípios - {disciplina_escolhida}",
    )
    fig_barra.update_traces(textposition="outside")
    fig_barra.update_layout(showlegend=False, yaxis_title="Quantidade")

    st.plotly_chart(fig_barra, use_container_width=True)

# ---------------------------
# ABA 2: GRÁFICOS DE PIZZA POR DISCIPLINA
# ---------------------------
with aba2:
    st.subheader("🥧 Distribuição interna por Disciplina e Município")

    indicadores = [c for c in df_total.columns if any(p in c.lower() for p in ["convocado", "eliminado", "reclass", "document", "total"])]

    if indicadores:
        indicador_escolhido = st.selectbox("Selecione o indicador:", indicadores)
    else:
        st.warning("Nenhuma coluna de indicador encontrada.")
        st.stop()

    # Gera um gráfico de pizza para cada município
    for municipio in municipios:
        df_mun = df_total[df_total["Município"] == municipio]
        if not df_mun.empty:
            st.markdown(f"### 📍 {municipio}")
            fig_pizza = px.pie(
                df_mun,
                names="Disciplina",
                values=indicador_escolhido,
                title=f"Distribuição de {indicador_escolhido} por Disciplina - {municipio}"
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.info(f"Sem dados disponíveis para {municipio}.")
