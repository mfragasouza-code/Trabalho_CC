import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Painel de Editais", layout="wide")

# --- FUNÇÃO PARA CARREGAR OS DADOS ---
@st.cache_data
def carregar_dados():
    arquivos = {
        "Vitória 40": "vitoria_40.xlsx",
        "Serra 40": "serra_40.xlsx",
        "Fundão 40": "fundao_40.xlsx",
        "Santa Teresa 40": "santa_teresa_40.xlsx",
        "Vitória 42": "vitoria_42.xlsx",
        "Serra 42": "serra_42.xlsx",
        "Fundão 42": "fundao_42.xlsx",
        "Santa Teresa 42": "santa_teresa_42.xlsx"
    }

    dados = {}
    for nome, arquivo in arquivos.items():
        df = pd.read_excel(f"layout/{arquivo}")
        dados[nome] = df
    return dados


# --- CARREGAR OS DADOS ---
dados_edital = carregar_dados()

# --- MENU LATERAL ---
st.sidebar.title("📊 Painel de Editais")
edital_numero = st.sidebar.selectbox("Selecione o edital:", ["40", "42"])
pagina = st.sidebar.radio("Navegar para:", ["Visão Geral", "Gráficos por Município", "Gráficos Município/Disciplina"])

st.sidebar.markdown("---")
st.sidebar.info("Use o menu acima para alternar entre as visualizações.")

# --- FILTRAR MUNICÍPIOS PELO EDITAL ---
municipios_filtrados = [k for k in dados_edital.keys() if edital_numero in k]

# --- CORES PADRONIZADAS ---
CORES_PADRAO = {
    "Convocados": "#1f77b4",
    "Reclassificados": "#0072B2",
    "Eliminados": "#56B4E9",
    "Contratados": "#D55E00",
    "Aguardando análise": "#E69F00",
    "Taxa de não resposta": "#CC79A7"
}


# ==============================
#  ABA 1 - VISÃO GERAL
# ==============================
if pagina == "Visão Geral":
    st.title("📋 Visão Geral dos Editais")
    st.write(f"Análise consolidada dos municípios do edital {edital_numero}/2024.")

    municipio_escolhido = st.selectbox("Selecione o município:", municipios_filtrados)

    df = dados_edital[municipio_escolhido]

    # Calcular taxa de não resposta
    if "Convocados" in df.columns and "Aguardando análise" in df.columns:
        df["Taxa de não resposta (%)"] = (
            1 - ((df["Aguardando análise"] + df["Contratados"]) / df["Convocados"])
        ) * 100

    st.dataframe(df.describe(include='all'), use_container_width=True)


# ==============================
#  ABA 2 - GRÁFICOS POR MUNICÍPIO
# ==============================
elif pagina == "Gráficos por Município":
    st.title("📈 Comparativo de Indicadores por Município")

    municipio_escolhido = st.selectbox("Selecione o município para visualizar:", municipios_filtrados)

    try:
        df = dados_edital[municipio_escolhido]

        fig = px.bar(
            df,
            x="Disciplina",
            y=["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Contratados"],
            barmode="group",
            color_discrete_map=CORES_PADRAO,
            title=f"{municipio_escolhido} - Edital {edital_numero}/2024"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao gerar gráfico para {municipio_escolhido}: {e}")


# ==============================
#  ABA 3 - GRÁFICOS MUNICÍPIO/DISCIPLINA
# ==============================
elif pagina == "Gráficos Município/Disciplina":
    st.title("📊 Análise por Município e Disciplina")

    municipio_escolhido = st.selectbox("Selecione o município:", municipios_filtrados)
    df = dados_edital[municipio_escolhido]

    disciplina_escolhida = st.selectbox("Selecione a disciplina:", df["Disciplina"].unique())

    linha = df[df["Disciplina"] == disciplina_escolhida].iloc[0]

    valores = {
        "Reclassificados": linha["Reclassificados"],
        "Eliminados": linha["Eliminados"],
        "Contratados": linha["Contratados"],
        "Aguardando análise": linha["Aguardando análise"]
    }

    # Calcular taxa de não resposta
    if linha["Convocados"] > 0:
        taxa_nao_resposta = (1 - ((linha["Contratados"] + linha["Aguardando análise"]) / linha["Convocados"])) * 100
    else:
        taxa_nao_resposta = 0

    valores["Taxa de não resposta"] = taxa_nao_resposta

    # Gráfico de pizza com cores padronizadas
    fig = px.pie(
        names=list(valores.keys()),
        values=list(valores.values()),
        color=list(valores.keys()),
        color_discrete_map=CORES_PADRAO,
        title=f"{disciplina_escolhida} - {municipio_escolhido}"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.metric("📉 Taxa de não resposta", f"{taxa_nao_resposta:.2f}%")
