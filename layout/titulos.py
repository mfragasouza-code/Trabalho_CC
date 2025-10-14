# ------------------------------------------------------------
# APP STREAMLIT - INDICADORES POR MUNICÍPIO E DISCIPLINA
# ------------------------------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ------------------------------------------------------------
# CONFIGURAÇÕES INICIAIS
# ------------------------------------------------------------
st.set_page_config(page_title="Indicadores - Editais 40 e 42/2024", layout="wide")

st.title("📊 Indicadores dos Editais 40/2024 e 42/2024")
st.markdown("""
Análise comparativa por **município** e **disciplina**, com base nos indicadores dos processos seletivos.  
**OBS:** No momento a base de dados é a mesma nos 2 editais e nos 4 municípios enquanto construímos o MVP.
""")

# ------------------------------------------------------------
# FUNÇÃO PARA CARREGAR OS DADOS
# ------------------------------------------------------------
def carregar_dados():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    arquivos = {
        "Vitória 40": os.path.join(BASE_DIR, "vitoria_40.xlsx"),
        "Serra 40": os.path.join(BASE_DIR, "serra_40.xlsx"),
        "Fundão 40": os.path.join(BASE_DIR, "fundao_40.xlsx"),
        "Santa Teresa 40": os.path.join(BASE_DIR, "santa_teresa_40.xlsx"),
        "Vitória 42": os.path.join(BASE_DIR, "vitoria_42.xlsx"),
        "Serra 42": os.path.join(BASE_DIR, "serra_42.xlsx"),
        "Fundão 42": os.path.join(BASE_DIR, "fundao_42.xlsx"),
        "Santa Teresa 42": os.path.join(BASE_DIR, "santa_teresa_42.xlsx"),
    }

    dados = {}
    for nome, caminho in arquivos.items():
        if os.path.exists(caminho):
            dados[nome] = pd.read_excel(caminho)
        else:
            print(f"⚠️ Arquivo não encontrado: {caminho}")
    return dados

dados_municipios = carregar_dados()

# ------------------------------------------------------------
# MENU LATERAL HIERÁRQUICO
# ------------------------------------------------------------
st.sidebar.title("📁 Menu de Navegação")

pagina_principal = st.sidebar.radio(
    "Selecione a seção:",
    ("Página Inicial", "Edital 40/2024", "Edital 42/2024")
)

# Submenu (só aparece quando um edital é selecionado)
if pagina_principal in ["Edital 40/2024", "Edital 42/2024"]:
    subpagina = st.sidebar.radio(
        "Subseções:",
        ("📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos de Pizza"),
        key=f"subpagina_{pagina_principal}"
    )
else:
    subpagina = None

# ------------------------------------------------------------
# PÁGINA INICIAL
# ------------------------------------------------------------
if pagina_principal == "Página Inicial":
    st.header("🏠 Página Inicial")
    st.markdown("""
    Este painel apresenta os **indicadores dos editais 40/2024 e 42/2024**,
    organizados por **município** e **disciplina**.  
    Use o menu lateral para navegar entre os editais e visualizar os gráficos.
    """)

# ------------------------------------------------------------
# FUNÇÃO PARA EXIBIR OS DADOS DE UM EDITAL
# ------------------------------------------------------------
def exibir_edital(edital_numero, subpagina):
    st.header(f"📘 Indicadores - Edital {edital_numero}/2024")

    dados_edital = {k: v for k, v in dados_municipios.items() if k.endswith(str(edital_numero))}
    if not dados_edital:
        st.warning("⚠️ Nenhum dado encontrado. Verifique os arquivos Excel.")
        return

    # ----------- VISÃO GERAL -----------
    if subpagina == "📈 Visão Geral":
        st.subheader("📊 Somatório dos Indicadores por Município")
        indicadores = ["Aguardando análise", "Reclassificados", "Eliminados", "Contratados"]

        resumo = []
        for municipio, df in dados_edital.items():
            soma = df[indicadores].sum(numeric_only=True)
            soma["Município"] = municipio
            resumo.append(soma)

        df_resumo = pd.DataFrame(resumo)
        fig_bar = px.bar(
            df_resumo.melt(id_vars="Município", var_name="Indicador", value_name="Total"),
            x="Município", y="Total", color="Indicador",
            title=f"Comparativo de Indicadores - Edital {edital_numero}/2024"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Tabela descritiva
        municipios_disponiveis = list(dados_edital.keys())
        municipio_escolhido = st.selectbox(
            "Selecione o município:",
            municipios_disponiveis,
            key=f"select_municipio_geral_{edital_numero}"
        )

        df = dados_edital[municipio_escolhido]
        st.markdown(f"### 📍 {municipio_escolhido}")
        st.dataframe(df.describe(include='all'))

    # ----------- GRÁFICOS COMPARATIVOS -----------
    elif subpagina == "📊 Gráficos Comparativos":
        st.subheader("📊 Comparativo de Indicadores Entre as Disciplinas")

        cidades_exibicao = [c.replace(f" {edital_numero}", "") for c in dados_edital.keys()]
        map_exib_to_chave = {exib: chave for exib, chave in zip(cidades_exibicao, dados_edital.keys())}

        municipio_escolhido_exib = st.selectbox(
            "Selecione o município para visualizar:",
            cidades_exibicao,
            key=f"select_municipio_barras_{edital_numero}"
        )

        municipio_chave = map_exib_to_chave[municipio_escolhido_exib]
        df = dados_edital[municipio_chave]

        fig = px.bar(
            df,
            x="Disciplina",
            y=["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Contratados"],
            barmode="group",
            title=f"{municipio_escolhido_exib} - Edital {edital_numero}/2024"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ----------- GRÁFICOS DE PIZZA + TAXA DE NÃO RESPOSTA -----------
    elif subpagina == "🥧 Gráficos de Pizza":
        st.subheader("🥧 Indicadores por Disciplina e Município")

        municipio_escolhido = st.selectbox(
            "Selecione o município:",
            list(dados_edital.keys()),
            key=f"select_municipio_pizza_{edital_numero}"
        )

        df = dados_edital[municipio_escolhido]
        disciplina_escolhida = st.selectbox(
            "Selecione a disciplina:",
            df["Disciplina"].unique().tolist(),
            key=f"select_disciplina_pizza_{edital_numero}"
        )

        linha = df[df["Disciplina"] == disciplina_escolhida].iloc[0]
        valores = linha[["Aguardando análise", "Eliminados", "Reclassificados", "Contratados"]]

        cores_padrao = {
            "Aguardando análise": "#FFCC00",
            "Eliminados": "#FF4C4C",
            "Reclassificados": "#0073E6",
            "Contratados": "#00B050"
        }

        fig_pizza = px.pie(
            values=valores.values,
            names=valores.index,
            title=f"{disciplina_escolhida} - {municipio_escolhido} ({edital_numero}/2024)",
            color=valores.index,
            color_discrete_map=cores_padrao
        )

        total_candidatos = linha["Total de candidatos"]
        documentos = linha["Documentos analisados"]
        convocados = linha["Convocados"]
        aguardando = linha["Aguardando análise"]

        if convocados > 0:
            taxa_nao_resposta = ((convocados - (documentos + aguardando)) / convocados) * 100
        else:
            taxa_nao_resposta = 0

        col1, col2 = st.columns([3, 1])
        with col1:
            st.plotly_chart(fig_pizza, use_container_width=True)
        with col2:
            st.markdown(f"**Total de candidatos:** {total_candidatos}")
            st.markdown(f"**Documentos analisados:** {documentos}")
            st.markdown(f"**Convocados:** {convocados}")
            st.markdown(f"**Aguardando análise:** {aguardando}")
            st.markdown(f"**📉 Taxa de não resposta:** {taxa_nao_resposta:.2f}%")

# ------------------------------------------------------------
# CHAMADA FINAL
# ------------------------------------------------------------
if pagina_principal == "Edital 40/2024":
    exibir_edital(40, subpagina)
elif pagina_principal == "Edital 42/2024":
    exibir_edital(42, subpagina)
