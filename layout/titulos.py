import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------
# CONFIGURAÇÃO INICIAL
# -------------------------------------------
st.set_page_config(page_title="Análise dos Editais", layout="wide")

st.title("📊 Painel de Análise dos Editais por Município")

# -------------------------------------------
# FUNÇÃO PARA LER TODAS AS ABAS DE UM EXCEL
# -------------------------------------------
def carregar_dados(caminho_arquivo):
    abas_excluir = ["AUX", "INDICE", "Log", "CHAMADA", "Configuração de Email"]
    xls = pd.ExcelFile(caminho_arquivo)
    dados = {}
    for aba in xls.sheet_names:
        if aba not in abas_excluir:
            df = pd.read_excel(xls, aba)
            dados[aba] = df
    return dados

# -------------------------------------------
# UPLOAD DOS 4 ARQUIVOS POR EDITAL
# -------------------------------------------
st.sidebar.header("📂 Upload dos Arquivos Excel")
st.sidebar.markdown("Envie os 4 arquivos (um por município) de um mesmo edital.")

municipios = ["Vitória", "Serra", "Santa Teresa", "Fundão"]

arquivos = {}
for m in municipios:
    arquivos[m] = st.sidebar.file_uploader(f"Arquivo de {m}", type=["xlsx"], key=m)

# -------------------------------------------
# LEITURA E ORGANIZAÇÃO DOS DADOS
# -------------------------------------------
dados_municipios = {}
for m in municipios:
    if arquivos[m]:
        dados_municipios[m] = carregar_dados(arquivos[m])

# -------------------------------------------
# ABA DE VISÃO GERAL
# -------------------------------------------
st.header("📈 Visão Geral")

aba = st.selectbox("Selecione o Município:", municipios)

if aba in dados_municipios:
    dfs = dados_municipios[aba]
    
    # Combinar todas as disciplinas em um único DataFrame
    df_total = pd.concat(dfs.values(), ignore_index=True)
    
    # Estatísticas gerais do município
    st.subheader(f"Estatísticas Gerais - {aba}")
    st.dataframe(df_total.describe())
    
    # Estatísticas por disciplina
    st.subheader("📊 Estatísticas por Disciplina")
    for disciplina, df in dfs.items():
        st.markdown(f"**Disciplina: {disciplina}**")
        st.dataframe(df.describe())
else:
    st.info("Envie os arquivos para visualizar os dados.")

# -------------------------------------------
# GRÁFICOS DE BARRAS COMPARATIVOS ENTRE MUNICÍPIOS
# -------------------------------------------
st.header("🏙️ Comparativo entre Municípios")

# Verifica se há dados de todos os municípios
if all(m in dados_municipios for m in municipios):
    # Combina os dados de todos os municípios em um único DataFrame
    lista_dfs = []
    for m in municipios:
        for disciplina, df in dados_municipios[m].items():
            df_temp = df.copy()
            df_temp["Município"] = m
            df_temp["Disciplina"] = disciplina
            lista_dfs.append(df_temp)
    df_comparativo = pd.concat(lista_dfs, ignore_index=True)
    
    # Selecionar disciplina para comparar
    disciplinas = df_comparativo["Disciplina"].unique()
    disciplina_selecionada = st.selectbox("Selecione uma disciplina para comparar:", disciplinas)
    
    df_disciplina = df_comparativo[df_comparativo["Disciplina"] == disciplina_selecionada]
    colunas_qtd = ["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Documentos analisados"]
    
    for coluna in colunas_qtd:
        if coluna in df_disciplina.columns:
            fig_bar = px.bar(df_disciplina, x="Município", y=coluna, color="Município",
                             title=f"{coluna} por Município - {disciplina_selecionada}",
                             labels={"y": "Quantidade"})
            st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("Envie os arquivos de todos os municípios para visualizar o comparativo.")

# -------------------------------------------
# GRÁFICOS DE PIZZA DE CADA DISCIPLINA POR MUNICÍPIO
# -------------------------------------------
st.header("🥧 Gráficos de Pizza por Município e Disciplina")

for m in municipios:
    if m in dados_municipios:
        st.subheader(f"{m}")
        for disciplina, df in dados_municipios[m].items():
            st.markdown(f"**Disciplina: {disciplina}**")
            if all(col in df.columns for col in ["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Documentos analisados"]):
                valores = df[["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Documentos analisados"]].sum()
                fig_pizza = px.pie(values=valores, names=valores.index,
                                   title=f"Distribuição - {disciplina} ({m})")
                st.plotly_chart(fig_pizza, use_container_width=True)
            else:
                st.warning(f"Algumas colunas estão faltando em {disciplina} ({m})")

# -------------------------------------------
# FIM
# -------------------------------------------
st.success("✅ Painel carregado com sucesso!")
