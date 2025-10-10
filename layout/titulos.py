import streamlit as st
import pandas as pd
import plotly.express as px

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
# ABA VISÃO GERAL
# ------------------------------------------------------------
st.header("📈 Visão Geral")

municipio_sel = st.selectbox("Selecione o município:", municipios)

if municipio_sel in dados_municipios and not dados_municipios[municipio_sel].empty:
    df = dados_municipios[municipio_sel]

    # Checa e exibe estatísticas gerais
    colunas_indicadores = ["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Documentos analisados"]
    colunas_presentes = [c for c in colunas_indicadores if c in df.columns]

    st.subheader(f"📊 Estatísticas Gerais - {municipio_sel}")
    st.dataframe(df[colunas_presentes].describe().T)

    st.subheader("📘 Estatísticas por Disciplina")
    st.dataframe(df[["Disciplina"] + colunas_presentes])
else:
    st.info("Envie os arquivos para visualizar as estatísticas.")

# ------------------------------------------------------------
# GRÁFICOS DE BARRAS COMPARATIVOS ENTRE MUNICÍPIOS
# ------------------------------------------------------------
st.header("🏙️ Comparativo de Disciplinas entre Municípios")

# Confirma se todos os municípios têm dados
if any(dados_municipios.values()):
    # Junta todos os dados
    lista_dfs = [df for df in dados_municipios.values() if not df.empty]
    df_comparativo = pd.concat(lista_dfs, ignore_index=True)

    # Seleciona disciplina
    disciplinas = df_comparativo["Disciplina"].unique()
    disciplina_sel = st.selectbox("Selecione a disciplina:", sorted(disciplinas))

    df_disciplina = df_comparativo[df_comparativo["Disciplina"] == disciplina_sel]

    colunas_indicadores = ["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Documentos analisados"]

    for coluna in colunas_indicadores:
        if coluna in df_disciplina.columns:
            fig_bar = px.bar(
                df_disciplina,
                x="Município",
                y=coluna,
                color="Município",
                title=f"{coluna} - {disciplina_sel}",
                labels={"y": "Quantidade", "x": "Município"}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("Envie pelo menos um arquivo para ver os comparativos.")

# ------------------------------------------------------------
# GRÁFICOS DE PIZZA POR MUNICÍPIO E DISCIPLINA
# ------------------------------------------------------------
st.header("🥧 Gráficos de Pizza - Indicadores por Disciplina e Município")

for m, df in dados_municipios.items():
    if not df.empty:
        st.subheader(f"{m}")
        for _, linha in df.iterrows():
            disciplina = linha["Disciplina"]
            valores = linha[["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Documentos analisados"]]
            fig_pizza = px.pie(
                values=valores.values,
                names=valores.index,
                title=f"{disciplina} - {m}"
            )
            st.plotly_chart(fig_pizza, use_container_width=True)

st.success("✅ Painel carregado com sucesso!")
