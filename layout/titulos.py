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
st.markdown("Análise comparativa por **município** e **disciplina**, com base nos indicadores dos processos seletivos.")
st.markdown("**OBSERVAÇÃO:** No momento a base de dados é a mesma nos 2 (dois) editais e nos 4 (quatro) municípios enquanto estamos construindo a estrutura do MVP.")

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


# ------------------------------------------------------------
# CARREGAMENTO DOS DADOS
# ------------------------------------------------------------
dados_municipios = carregar_dados()

# ------------------------------------------------------------
# MENU LATERAL
# ------------------------------------------------------------
st.sidebar.title("📁 Menu de Navegação")
pagina = st.sidebar.radio(
    "Selecione a página:",
    ("Página Inicial", "Edital 40/2024", "Edital 42/2024")
)

# ------------------------------------------------------------
# PÁGINA INICIAL
# ------------------------------------------------------------
if pagina == "Página Inicial":
    st.header("🏠 Página Inicial")
    st.markdown("""
    Este painel apresenta os **indicadores dos editais 40/2024 e 42/2024**,
    organizados por **município** e **disciplina**.  
    Utilize o menu lateral para navegar entre os editais e visualizar os gráficos.
    """)


# ------------------------------------------------------------
# FUNÇÃO PARA EXIBIR OS DADOS DE UM EDITAL
# ------------------------------------------------------------
def exibir_edital(edital_numero):
    st.header(f"📘 Indicadores - Edital {edital_numero}/2024")
    st.markdown(f"Análise dos indicadores do **Edital {edital_numero}/2024**, por município e disciplina.")

    # Selecionar os dados do edital
    dados_edital = {k: v for k, v in dados_municipios.items() if k.endswith(str(edital_numero))}

    if not dados_edital:
        st.warning("⚠️ Nenhum dado carregado. Verifique os arquivos Excel.")
        return

    # Verificar se algum arquivo está faltando
    municipios_faltando = [m for m in ["Vitória", "Serra", "Fundão", "Santa Teresa"] if f"{m} {edital_numero}" not in dados_edital]
    if municipios_faltando:
        st.error(f"🚨 Alguns arquivos de dados não foram encontrados: {', '.join(municipios_faltando)}")
        return

    # Criar abas
    aba_geral, aba_barras, aba_pizza = st.tabs(["📋 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos de Pizza"])

    # ------------------------------------------------------------
    # ABA 1: VISÃO GERAL
    # ------------------------------------------------------------
    with aba_geral:
        st.subheader("📈 Somatório dos Indicadores por Município")
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

        # 📋 Selecionar município
        st.subheader("📋 Tabela Descritiva por Município")
        municipios_disponiveis = list(dados_edital.keys())

        municipio_escolhido = st.selectbox(
            "Selecione o município:",
            municipios_disponiveis,
            key=f"select_municipio_geral_{edital_numero}"
        )

        if municipio_escolhido:
            df = dados_edital[municipio_escolhido]
            st.markdown(f"### 📍 {municipio_escolhido}")
            st.dataframe(df.describe(include='all'))

            with st.expander("📄 Ver dados completos do município selecionado"):
                st.dataframe(df)

    # ------------------------------------------------------------
    # ABA 2: GRÁFICOS COMPARATIVOS
    # ------------------------------------------------------------
    with aba_barras:
        st.subheader("📊 Comparativo de Indicadores Entre as Disciplinas do Município")

        cidades_chave = list(dados_edital.keys())
        cidades_exibicao = [c.replace(f" {edital_numero}", "") for c in cidades_chave]
        map_exib_to_chave = {exib: chave for exib, chave in zip(cidades_exibicao, cidades_chave)}

        municipio_escolhido_exib = st.selectbox(
            "Selecione o município para visualizar:",
            cidades_exibicao,
            key=f"select_municipio_barras_{edital_numero}"
        )

        if municipio_escolhido_exib:
            municipio_chave = map_exib_to_chave[municipio_escolhido_exib]
            df = dados_edital[municipio_chave]

            try:
                fig = px.bar(
                    df,
                    x="Disciplina",
                    y=["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Contratados"],
                    barmode="group",
                    title=f"{municipio_escolhido_exib} - Edital {edital_numero}/2024"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar gráfico para {municipio_escolhido_exib}: {e}")

    # ------------------------------------------------------------
    # ABA 3: GRÁFICOS DE PIZZA + TAXA DE NÃO RESPOSTA
    # ------------------------------------------------------------
    with aba_pizza:
        st.subheader("🥧 Gráficos de Pizza - Indicadores por Disciplina e Município")

        municipios_disponiveis = list(dados_edital.keys())
        municipio_escolhido_exib = st.selectbox(
            "Selecione o município:",
            municipios_disponiveis,
            key=f"select_municipio_pizza_{edital_numero}"
        )

        if municipio_escolhido_exib:
            df = dados_edital[municipio_escolhido_exib]
            disciplinas_disponiveis = df["Disciplina"].unique().tolist()

            disciplina_escolhida = st.selectbox(
                "Selecione a disciplina:",
                disciplinas_disponiveis,
                key=f"select_disciplina_pizza_{edital_numero}"
            )

            if disciplina_escolhida:
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
                    title=f"{disciplina_escolhida} - {municipio_escolhido_exib} ({edital_numero}/2024)",
                    color=valores.index,
                    color_discrete_map=cores_padrao
                )

                total_candidatos = linha["Total de candidatos"]
                convocados = linha["Convocados"]
                aguardando = linha["Aguardando análise"]
                documentos = linha["Documentos analisados"]

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
# CHAMADA DE CADA EDITAL
# ------------------------------------------------------------
if pagina == "Edital 40/2024":
    exibir_edital(40)
elif pagina == "Edital 42/2024":
    exibir_edital(42)
