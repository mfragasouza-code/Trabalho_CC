import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# ===========================
# CONFIGURAÇÕES INICIAIS
# ===========================
st.set_page_config(
    page_title="Painel de Contratação",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Painel Interativo de Contratação")
st.markdown(
    """
    Este painel apresenta dados atualizados sobre o processo de contratação,
    com filtros dinâmicos e visualizações interativas.
    """
)

# ===========================
# CARREGAR PLANILHA
# ===========================
@st.cache_data
def carregar_dados():
    df = pd.read_excel("Resumo_Geral.xlsx")

    # Excluir colunas indesejadas
    colunas_excluir = ["Ampla Concorrência", "Negros", "Deficientes", "Indígenas"]
    df = df.drop(columns=[c for c in colunas_excluir if c in df.columns], errors="ignore")

    return df

df = carregar_dados()

# ===========================
# FILTROS LATERAIS
# ===========================
st.sidebar.header("🔎 Filtros de Dados")

colunas_texto = df.select_dtypes(include=["object"]).columns.tolist()
colunas_num = df.select_dtypes(exclude=["object"]).columns.tolist()

filtros = {}
for col in colunas_texto:
    valores = sorted(df[col].dropna().unique().tolist())
    escolha = st.sidebar.multiselect(f"{col}:", valores)
    if escolha:
        filtros[col] = escolha

for col in colunas_num:
    min_val, max_val = df[col].min(), df[col].max()
    faixa = st.sidebar.slider(f"{col}:", float(min_val), float(max_val), (float(min_val), float(max_val)))
    filtros[col] = faixa

df_filtrado = df.copy()
for col, val in filtros.items():
    if col in colunas_texto:
        df_filtrado = df_filtrado[df_filtrado[col].isin(val)]
    elif col in colunas_num:
        df_filtrado = df_filtrado[df_filtrado[col].between(val[0], val[1])]

st.sidebar.success(f"{len(df_filtrado)} registros exibidos após filtro.")

# ===========================
# ABAS PRINCIPAIS
# ===========================
aba1, aba2, aba3, aba4 = st.tabs([
    "📈 Visão Geral",
    "📊 Gráficos Interativos",
    "📋 Tabela Completa",
    "📥 Download"
])

# ===========================
# ABA 1 - VISÃO GERAL
# ===========================
with aba1:
    st.subheader("📌 Estatísticas Resumidas")
    st.dataframe(df_filtrado.describe(include="all"), use_container_width=True)

    # Exemplo: contar registros por coluna de interesse
    st.subheader("📍 Quantidade de registros por categoria")
    colunas_categ = [c for c in df_filtrado.columns if df_filtrado[c].nunique() < 20]
    if colunas_categ:
        cat_col = st.selectbox("Escolha uma categoria:", colunas_categ)
        contagem = df_filtrado[cat_col].value_counts().reset_index()
        contagem.columns = [cat_col, "Quantidade"]
        fig = px.bar(contagem, x=cat_col, y="Quantidade", text="Quantidade", color=cat_col)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma coluna categórica adequada para contagem.")

# ===========================
# ABA 2 - GRÁFICOS INTERATIVOS
# ===========================
with aba2:
    st.subheader("📊 Comparações Personalizadas")

    colunas_disp = df_filtrado.columns.tolist()
    col1, col2 = st.columns(2)
    with col1:
        eixo_x = st.selectbox("Eixo X:", colunas_disp, key="x")
    with col2:
        eixo_y = st.selectbox("Eixo Y:", colunas_disp, key="y")

    tipo_grafico = st.radio(
        "Selecione o tipo de gráfico:",
        ["Barras", "Dispersão", "Pizza"],
        horizontal=True
    )

    if eixo_x and eixo_y:
        if tipo_grafico == "Barras":
            fig = px.bar(df_filtrado, x=eixo_x, y=eixo_y, color=eixo_x, title=f"{eixo_y} por {eixo_x}")
        elif tipo_grafico == "Dispersão":
            fig = px.scatter(df_filtrado, x=eixo_x, y=eixo_y, color=eixo_x, title=f"{eixo_y} vs {eixo_x}")
        elif tipo_grafico == "Pizza":
            fig = px.pie(df_filtrado, names=eixo_x, values=eixo_y, title=f"Distribuição de {eixo_y} por {eixo_x}")

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Selecione as colunas para gerar o gráfico.")

# ===========================
# ABA 3 - TABELA COMPLETA
# ===========================
with aba3:
    st.subheader("📋 Dados Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

# ===========================
# ABA 4 - DOWNLOAD
# ===========================
with aba4:
    st.subheader("📥 Exportar Dados Filtrados")

    def converter_para_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Filtrado')
        return output.getvalue()

    dados_excel = converter_para_excel(df_filtrado)

    st.download_button(
        label="⬇️ Baixar arquivo Excel",
        data=dados_excel,
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("Clique no botão acima para baixar a versão filtrada dos dados.")

