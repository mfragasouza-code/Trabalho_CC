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
# CRIAÇÃO DAS ABAS
# ------------------------------------------------------------
aba_geral, aba_barras, aba_pizza = st.tabs([
    "📊 Visão Geral",
    "🏙️ Gráficos Comparativos entre Municípios",
    "🥧 Gráficos de Pizza por Município e Disciplina"
])

# ------------------------------------------------------------
# 📊 ABA 1 — VISÃO GERAL
# ------------------------------------------------------------
with aba_geral:
    st.header("📊 Visão Geral das Disciplinas por Município")

    for m, df in dados_municipios.items():
        if not df.empty:
            st.subheader(f"📍 {m}")
            
            # Padroniza os nomes das colunas
            df.columns = df.columns.str.strip().str.lower()

            # Estatísticas básicas por disciplina
            st.dataframe(df.describe(include='all'))

            # Gráfico de barras por disciplina
            col_disciplina = next((c for c in df.columns if "disciplina" in c), None)
            col_total = next((c for c in df.columns if "total" in c and "candidato" in c), None)

            if col_disciplina and col_total:
                fig_total = px.bar(
                    df,
                    x=col_disciplina,
                    y=col_total,
                    title=f"Total de Candidatos por Disciplina - {m}",
                    labels={"x": "Disciplina", "y": "Quantidade"}
                )
                st.plotly_chart(fig_total, use_container_width=True)

# ------------------------------------------------------------
# 🏙️ ABA 2 — GRÁFICOS DE BARRAS COMPARATIVOS
# ------------------------------------------------------------
with aba_barras:
    st.header("🏙️ Comparativo de Disciplinas entre Municípios")

    # Criação de base consolidada
    dfs_renomeados = []
    for m, df in dados_municipios.items():
        if not df.empty:
            df = df.copy()
            df.columns = df.columns.str.strip().str.lower()
            col_disciplina = next((c for c in df.columns if "disciplina" in c), None)
            col_total = next((c for c in df.columns if "total" in c and "candidato" in c), None)
            if col_disciplina and col_total:
                df["município"] = m
                dfs_renomeados.append(df[[col_disciplina, col_total, "município"]])

    if dfs_renomeados:
        df_comparativo = pd.concat(dfs_renomeados)
        fig_comp = px.bar(
            df_comparativo,
            x="disciplina",
            y=col_total,
            color="município",
            barmode="group",
            title="Comparativo de Candidatos por Disciplina entre Municípios",
            labels={"disciplina": "Disciplina", "quantidade": "Quantidade"}
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# ------------------------------------------------------------
# GRÁFICOS DE PIZZA POR MUNICÍPIO E DISCIPLINA
# ------------------------------------------------------------
with aba3:
    st.header("🥧 Gráficos de Pizza - Indicadores por Disciplina e Município")

    for m, df in dados_municipios.items():
        if not df.empty:
            st.subheader(f"{m}")

            for _, linha in df.iterrows():
                disciplina = linha["Disciplina"]

                # Fatias da pizza (sem total e sem documentos analisados)
                valores = linha[["Aguardando análise", "Eliminados", "Reclassificados"]]

                # Indicadores complementares
                total_candidatos = linha["Total de candidatos"]
                documentos_analisados = linha["Documentos analisados"]
                convocados = linha["Convocados"]

                # Criar gráfico de pizza
                fig_pizza = px.pie(
                    values=valores.values,
                    names=valores.index,
                    title=f"{disciplina} - {m}",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )

                # Layout de duas colunas — gráfico + indicadores
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.plotly_chart(fig_pizza, use_container_width=True)
                with col2:
                    st.markdown(f"**📘 Disciplina:** {disciplina}")
                    st.markdown(f"**👥 Total de candidatos:** {int(total_candidatos)}")
                    st.markdown(f"**📄 Documentos analisados:** {int(documentos_analisados)}")
                    st.markdown(f"**📋 Convocados:** {int(convocados)}")
