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

st.title("📊 Indicadores dos Editais 40/2024 e 42/2024 da SRE Carapina")
st.markdown("Análise comparativa por **município** e **disciplina**, com base nos indicadores dos processos seletivos.")
st.markdown("Por Mirella Fraga")
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
# MENU LATERAL SIMPLES (apenas seleção de edital)
# ------------------------------------------------------------
st.sidebar.title("📁 Menu de Navegação")

pagina = st.sidebar.radio(
    "Selecione o edital:",
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
    Utilize o menu lateral para selecionar o edital.
    """)

# ------------------------------------------------------------
# FUNÇÃO PARA EXIBIR OS DADOS DE UM EDITAL
# ------------------------------------------------------------
elif pagina in ["Edital 40/2024", "Edital 42/2024"]:
    numero_edital = 40 if "40" in pagina else 42
    st.header(f"📘 Indicadores - {pagina}")
    st.markdown(f"Análise dos indicadores do **{pagina}**, por município e disciplina.")

    # Filtra os dados do edital selecionado
    dados_edital = {k: v for k, v in dados_municipios.items() if k.endswith(str(numero_edital))}

    if not dados_edital:
        st.warning("⚠️ Nenhum dado carregado. Verifique os arquivos Excel.")
    else:
        # Abas fixas na interface principal
        aba_geral, aba_barras, aba_pizza = st.tabs(
            ["📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"]
        )

        # ------------------------------------------------------------
        # ABA 1: VISÃO GERAL
        # ------------------------------------------------------------
        with aba_geral:
            st.subheader("📈 Indicadores Globais por Município")
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
                title=f"Comparativo de Indicadores - Edital {numero_edital}/2024"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # ------------------------------------------------------------
        # ABA 2: GRÁFICOS COMPARATIVOS
        # ------------------------------------------------------------
        with aba_barras:
            st.subheader("📊 Comparativo de Indicadores Entre as Disciplinas do Município")

            cidades_chave = list(dados_edital.keys())
            cidades_exibicao = [c.replace(f" {numero_edital}", "") for c in cidades_chave]
            map_exib_to_chave = {exib: chave for exib, chave in zip(cidades_exibicao, cidades_chave)}

            municipio_escolhido_exib = st.selectbox(
                "Selecione o município:",
                cidades_exibicao,
                key=f"select_municipio_barras_{numero_edital}"
            )

            if municipio_escolhido_exib:
                municipio_chave = map_exib_to_chave[municipio_escolhido_exib]
                df = dados_edital[municipio_chave]

                fig = px.bar(
                    df,
                    x="Disciplina",
                    y=["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Contratados"],
                    barmode="group",
                    title=f"{municipio_escolhido_exib} - Edital {numero_edital}/2024"
                )
                st.plotly_chart(fig, use_container_width=True)

        # ------------------------------------------------------------
        # ABA 3: GRÁFICOS DE PIZZA
        # ------------------------------------------------------------
        with aba_pizza:
            st.subheader("🥧 Indicadores por Disciplina e Município")

            municipios_disponiveis = list(dados_edital.keys())
            municipio_escolhido_exib = st.selectbox(
                "Selecione o município:",
                municipios_disponiveis,
                key=f"select_municipio_pizza_{numero_edital}"
            )

            if municipio_escolhido_exib:
                df = dados_edital[municipio_escolhido_exib]
                disciplinas_disponiveis = df["Disciplina"].unique().tolist()

                disciplina_escolhida = st.selectbox(
                    "Selecione a disciplina:",
                    disciplinas_disponiveis,
                    key=f"select_disciplina_pizza_{numero_edital}"
                )

                if disciplina_escolhida:
                    linha = df[df["Disciplina"] == disciplina_escolhida].iloc[0]
                    valores = linha[["Aguardando análise", "Eliminados", "Reclassificados", "Contratados"]]

                    fig_pizza = px.pie(
                        values=valores.values,
                        names=valores.index,
                        title=f"{disciplina_escolhida} - {municipio_escolhido_exib} ({numero_edital}/2024)"
                    )

                    st.plotly_chart(fig_pizza, use_container_width=True)
