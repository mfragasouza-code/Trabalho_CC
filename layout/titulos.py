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
            st.warning(f"⚠️ Arquivo não encontrado: {nome}")
    return dados

dados_municipios = carregar_dados()

# ------------------------------------------------------------
# CONFIGURAÇÃO DE ESTADO INICIAL
# ------------------------------------------------------------
if "edital" not in st.session_state:
    st.session_state["edital"] = "40"
if "aba" not in st.session_state:
    st.session_state["aba"] = "📈 Visão Geral"

# ------------------------------------------------------------
# MENU LATERAL SINCRONIZADO
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("## 📁 Menu de Navegação")
    edital = st.radio(
        "Selecione o edital:",
        ["40", "43"],
        index=0 if st.session_state["edital"] == "40" else 1,
        key="edital_radio"
    )
    st.session_state["edital"] = edital

    st.divider()
    aba_menu = st.radio(
        "Selecione a seção:",
        ("📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"),
        index=["📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"].index(st.session_state["aba"]),
        key="aba_menu"
    )
    st.session_state["aba"] = aba_menu

# ------------------------------------------------------------
# CONTEÚDO PRINCIPAL
# ------------------------------------------------------------
numero_edital = int(st.session_state["edital"])
dados_edital = {k: v for k, v in dados_municipios.items() if k.endswith(str(numero_edital))}

if not dados_edital:
    st.warning("⚠️ Nenhum dado encontrado. Verifique os arquivos Excel.")
else:
    st.header(f"📘 Indicadores - Edital {numero_edital}/2024")
    abas = st.tabs(["📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"])
    aba_labels = ["📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"]
    aba_index = aba_labels.index(st.session_state["aba"])

    # Se o usuário clicar numa aba, sincroniza automaticamente com o menu lateral
    for i, aba_nome in enumerate(abas):
        with aba_nome:
            if i == aba_index:
                st.session_state["aba"] = aba_labels[i]

                # ------------------------------------------------------------
                # VISÃO GERAL
                # ------------------------------------------------------------
                if st.session_state["aba"] == "📈 Visão Geral":
                    st.subheader("📈 Indicadores Globais por Município")
                    indicadores = ["Aguardando análise", "Reclassificados", "Eliminados", "Contratados"]
                    resumo = []
                    for municipio, df in dados_edital.items():
                        soma = df[indicadores].sum(numeric_only=True)
                        soma["Município"] = municipio.replace(f" {numero_edital}", "")
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
                elif st.session_state["aba"] == "📊 Gráficos Comparativos":
                    st.subheader("📊 Comparativo de Indicadores Entre Disciplinas do Município")
                    municipios = [c.replace(f" {numero_edital}", "") for c in dados_edital.keys()]
                    selecionado = st.selectbox("Selecione o município:", municipios)
                    if selecionado:
                        df = dados_edital[f"{selecionado} {numero_edital}"]
                        fig = px.bar(
                            df,
                            x="Disciplina",
                            y=["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Contratados"],
                            barmode="group",
                            title=f"{selecionado} - Edital {numero_edital}/2024"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                # ------------------------------------------------------------
                # GRÁFICOS MUNICÍPIO / DISCIPLINA
                # ------------------------------------------------------------
                elif st.session_state["aba"] == "🥧 Gráficos Município/Disciplina":
                    st.subheader("🥧 Indicadores por Disciplina e Município")
                    municipios = [c.replace(f" {numero_edital}", "") for c in dados_edital.keys()]
                    municipio_sel = st.selectbox("Selecione o município:", municipios)
                    if municipio_sel:
                        df = dados_edital[f"{municipio_sel} {numero_edital}"]
                        disciplinas = df["Disciplina"].unique().tolist()
                        disciplina_sel = st.selectbox("Selecione a disciplina:", disciplinas)
                        if disciplina_sel:
                            linha = df[df["Disciplina"] == disciplina_sel].iloc[0]
                            valores = linha[["Aguardando análise", "Eliminados", "Reclassificados", "Contratados"]]
                            fig_pizza = px.pie(
                                values=valores.values,
                                names=valores.index,
                                title=f"{disciplina_sel} - {municipio_sel} ({numero_edital}/2024)"
                            )
                            st.plotly_chart(fig_pizza, use_container_width=True)
