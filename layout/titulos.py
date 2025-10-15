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
st.set_page_config(
    page_title="Indicadores - Editais 40 e 43/2024",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# TÍTULO PRINCIPAL
# ------------------------------------------------------------
st.title("📊 Indicadores dos Editais 40/2024 e 43/2024 - SRE Carapina")
st.markdown("""
Análise comparativa por **município** e **disciplina**, com base nos indicadores dos processos seletivos.  
Por *Mirella Fraga*  
**Obs.:** Base de dados temporária e unificada enquanto o MVP é desenvolvido.
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
        "Vitória 43": os.path.join(BASE_DIR, "vitoria_43.xlsx"),
        "Serra 43": os.path.join(BASE_DIR, "serra_43.xlsx"),
        "Fundão 43": os.path.join(BASE_DIR, "fundao_43.xlsx"),
        "Santa Teresa 43": os.path.join(BASE_DIR, "santa_teresa_43.xlsx"),
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
# MENU LATERAL HIERÁRQUICO E SINCRONIZADO
# ------------------------------------------------------------
if "menu_principal" not in st.session_state:
    st.session_state["menu_principal"] = "Página Inicial"
if "subpagina" not in st.session_state:
    st.session_state["subpagina"] = "📈 Visão Geral"

with st.sidebar:
    st.markdown("## 📁 Menu de Navegação")
    with st.expander("🌍 Selecione o Edital", expanded=True):
        menu_principal = st.radio(
            "Escolha o edital:",
            ("Página Inicial", "Edital 40/2024", "Edital 43/2024"),
            key="menu_principal_radio",
            index=["Página Inicial", "Edital 40/2024", "Edital 43/2024"].index(st.session_state["menu_principal"])
        )

    subpagina = None
    if menu_principal in ["Edital 40/2024", "Edital 43/2024"]:
        with st.expander(f"📘 {menu_principal} - Seções", expanded=True):
            subpagina = st.radio(
                "Navegue entre as seções:",
                ("📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"),
                key="subpagina_radio",
                index=["📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"].index(st.session_state["subpagina"])
            )

    st.session_state["menu_principal"] = menu_principal
    if subpagina:
        st.session_state["subpagina"] = subpagina


# ------------------------------------------------------------
# PÁGINA INICIAL
# ------------------------------------------------------------
if st.session_state["menu_principal"] == "Página Inicial":
    st.header("🏠 Página Inicial")
    st.markdown("""
    Bem-vindo ao **Painel Interativo de Indicadores dos Editais 40/2024 e 43/2024** da SRE Carapina.  
    Aqui você poderá visualizar:
    - 📈 Indicadores gerais por município;  
    - 📊 Gráficos comparativos por disciplina;  
    - 🥧 Distribuições detalhadas por município e disciplina.  

    Use o menu lateral ou as abas superiores para navegar.
    """)


# ------------------------------------------------------------
# FUNÇÃO PARA EXIBIR CADA EDITAL
# ------------------------------------------------------------
elif st.session_state["menu_principal"] in ["Edital 40/2024", "Edital 43/2024"]:
    numero_edital = 40 if "40" in st.session_state["menu_principal"] else 43
    st.header(f"📘 Indicadores - {st.session_state['menu_principal']}")
    st.markdown(f"Análise dos indicadores do **{st.session_state['menu_principal']}**, por município e disciplina.")

    # Filtrar dados do edital
    dados_edital = {k: v for k, v in dados_municipios.items() if k.endswith(str(numero_edital))}

    if not dados_edital:
        st.warning("⚠️ Nenhum dado encontrado. Verifique os arquivos Excel.")
    else:
        abas = st.tabs(["📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"])
        abas_dict = {
            "📈 Visão Geral": abas[0],
            "📊 Gráficos Comparativos": abas[1],
            "🥧 Gráficos Município/Disciplina": abas[2]
        }

        # ------------------------------------------------------------
        # VISÃO GERAL
        # ------------------------------------------------------------
        with abas_dict["📈 Visão Geral"]:
            if st.session_state["subpagina"] == "📈 Visão Geral":
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
        # GRÁFICOS COMPARATIVOS
        # ------------------------------------------------------------
        with abas_dict["📊 Gráficos Comparativos"]:
            if st.session_state["subpagina"] == "📊 Gráficos Comparativos":
                st.subheader("📊 Comparativo de Indicadores Entre Disciplinas do Município")

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
        # GRÁFICOS MUNICÍPIO / DISCIPLINA + TAXA DE NÃO RESPOSTA
        # ------------------------------------------------------------
        with abas_dict["🥧 Gráficos Município/Disciplina"]:
            if st.session_state["subpagina"] == "🥧 Gráficos Município/Disciplina":
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

                        total_candidatos = linha["Total de candidatos"]
                        convocados = linha["Convocados"]
                        aguardando = linha["Aguardando análise"]
                        documentos = linha["Documentos analisados"]

                        taxa_nao_resposta = 0
                        if convocados > 0:
                            taxa_nao_resposta = ((convocados - (documentos + aguardando)) / convocados) * 100

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.plotly_chart(fig_pizza, use_container_width=True)
                        with col2:
                            st.markdown(f"**Total de candidatos:** {total_candidatos}")
                            st.markdown(f"**Convocados:** {convocados}")
                            st.markdown(f"**Aguardando análise:** {aguardando}")
                            st.markdown(f"**Documentos analisados:** {documentos}")
                            st.markdown(f"**📉 Taxa de não resposta:** {taxa_nao_resposta:.2f}%")

# ------------------------------------------------------------
# SINCRONIZAÇÃO AUTOMÁTICA ENTRE MENU E ABAS
# ------------------------------------------------------------
if st.session_state["menu_principal"] in ["Edital 40/2024", "Edital 43/2024"]:
    for nome, aba in abas_dict.items():
        if aba and aba.title == st.session_state["subpagina"]:
            st.session_state["subpagina"] = nome
