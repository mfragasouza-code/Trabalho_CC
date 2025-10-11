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
        "além de uma tabela descritiva gerada automaticamente com o método `describe()`."
    )

    # Colunas principais
    colunas_interesse = [
        "Total de candidatos",
        "Aguardando análise",
        "Eliminados",
        "Reclassificados",
        "Contratados",
        "Documentos analisados",
        "Convocados"
    ]

    # Loop pelos municípios
    for municipio, df_mun in dados_municipios.items():
        if not df_mun.empty:
            st.subheader(f"🏙️ {municipio}")

            # --- 1️⃣ TABELA DESCRITIVA DA BASE ---
            st.markdown("#### 📋 Estatísticas descritivas da base de dados")
            try:
                st.dataframe(df_mun[colunas_interesse].describe().T, use_container_width=True)
            except Exception as e:
                st.warning(f"Não foi possível gerar a descrição: {e}")

            # --- 2️⃣ SOMATÓRIO E GRÁFICO DE BARRAS ---
            st.markdown("#### 📊 Totais gerais por indicador")
            soma_municipio = df_mun[colunas_interesse].sum().reset_index()
            soma_municipio.columns = ["Indicador", "Quantidade"]
            st.dataframe(soma_municipio, use_container_width=True)

            # Gráfico usando o Streamlit nativo
            st.bar_chart(
                soma_municipio.set_index("Indicador"),
                y="Quantidade",
                height=400
            )

            st.markdown("---")
