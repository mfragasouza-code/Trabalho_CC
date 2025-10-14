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

# ------------------------------------------------------
# ⚙️ Função principal por edital
# ------------------------------------------------------
def exibir_edital(edital_numero):
    dados_edital = dados.get(str(edital_numero), {})
    st.title(f"📘 Indicadores - Edital {edital_numero}/2024")
    st.write(f"Análise dos indicadores do **Edital {edital_numero}/2024**, por município e disciplina.")

    # --- Sincronização entre menu lateral e abas superiores ---
    key_active = f"active_section_{edital_numero}"
    if key_active not in st.session_state:
        st.session_state[key_active] = "📈 Visão Geral"

    # função para atualizar a variável principal quando muda o radio do sidebar
    def _on_sidebar_change(ed=edital_numero):
        st.session_state[f"active_section_{ed}"] = st.session_state[f"sidebar_section_{ed}"]

    # radio lateral (subseções do edital)
    st.sidebar.subheader(f"🗂️ Edital {edital_numero}/2024 - Seções")
    if f"sidebar_section_{edital_numero}" not in st.session_state:
        st.session_state[f"sidebar_section_{edital_numero}"] = st.session_state[key_active]

    st.sidebar.radio(
        "Navegue entre as seções:",
        ("📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"),
        key=f"sidebar_section_{edital_numero}",
        on_change=_on_sidebar_change
    )

    # botões horizontais que funcionam como abas visuais
    tab_options = ["📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"]
    cols = st.columns([1, 1, 1])
    for c, opt in zip(cols, tab_options):
        with c:
            if st.session_state[key_active] == opt:
                btn_label = f"**{opt}**"
            else:
                btn_label = opt
            if st.button(btn_label, key=f"top_{edital_numero}_{opt}"):
                st.session_state[key_active] = opt
                st.session_state[f"sidebar_section_{edital_numero}"] = opt
                st.experimental_rerun()

    # variável que controla o conteúdo exibido
    active = st.session_state[key_active]

    # ------------------------------------------------------
    # 📈 SEÇÃO 1 - VISÃO GERAL
    # ------------------------------------------------------
    if active == "📈 Visão Geral":
        st.subheader("📈 Indicadores Globais por Município")
        indicadores = ["Aguardando análise", "Reclassificados", "Eliminados", "Contratados"]
        resumo = []
        for municipio, df in dados_edital.items():
            cols_ok = [c for c in indicadores if c in df.columns]
            soma = df[cols_ok].sum(numeric_only=True) if cols_ok else pd.Series(dtype=float)
            soma["Município"] = municipio
            resumo.append(soma)
        if resumo:
            df_resumo = pd.DataFrame(resumo).fillna(0)
            fig_bar = px.bar(
                df_resumo.melt(id_vars="Município", var_name="Indicador", value_name="Total"),
                x="Município", y="Total", color="Indicador",
                title=f"Comparativo de Indicadores - Edital {edital_numero}/2024"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Nenhum indicador disponível para exibir.")

    # ------------------------------------------------------
    # 📊 SEÇÃO 2 - GRÁFICOS COMPARATIVOS
    # ------------------------------------------------------
    elif active == "📊 Gráficos Comparativos":
        st.subheader("📊 Comparativo de Indicadores Entre Disciplinas do Município")
        cidades_chave = list(dados_edital.keys())
        cidades_exibicao = [c.replace(f" {edital_numero}", "") for c in cidades_chave]
        map_exib_to_chave = {exib: chave for exib, chave in zip(cidades_exibicao, cidades_chave)}

        municipio_escolhido_exib = st.selectbox(
            "Selecione o município:",
            cidades_exibicao,
            key=f"select_municipio_barras_{edital_numero}"
        )

        if municipio_escolhido_exib:
            municipio_chave = map_exib_to_chave[municipio_escolhido_exib]
            df = dados_edital[municipio_chave]
            colunas_y = ["Total de candidatos", "Convocados", "Eliminados", "Reclassificados", "Contratados"]
            colunas_validas = [c for c in colunas_y if c in df.columns]
            if colunas_validas and "Disciplina" in df.columns:
                fig = px.bar(
                    df,
                    x="Disciplina",
                    y=colunas_validas,
                    barmode="group",
                    title=f"{municipio_escolhido_exib} - Edital {edital_numero}/2024"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Colunas necessárias (Disciplina e indicadores) não foram encontradas neste arquivo.")

    # ------------------------------------------------------
    # 🥧 SEÇÃO 3 - GRÁFICOS POR MUNICÍPIO/DISCIPLINA
    # ------------------------------------------------------
    elif active == "🥧 Gráficos Município/Disciplina":
        st.subheader("🥧 Indicadores por Disciplina e Município")
        municipios_disponiveis = list(dados_edital.keys())
        municipio_escolhido_exib = st.selectbox(
            "Selecione o município:",
            municipios_disponiveis,
            key=f"select_municipio_pizza_{edital_numero}"
        )

        if municipio_escolhido_exib:
            df = dados_edital[municipio_escolhido_exib]
            if "Disciplina" not in df.columns:
                st.error("Coluna 'Disciplina' não encontrada neste arquivo.")
            else:
                disciplinas_disponiveis = df["Disciplina"].unique().tolist()
                disciplina_escolhida = st.selectbox(
                    "Selecione a disciplina:",
                    disciplinas_disponiveis,
                    key=f"select_disciplina_pizza_{edital_numero}"
                )

                if disciplina_escolhida:
                    linha = df[df["Disciplina"] == disciplina_escolhida].iloc[0]
                    campos = ["Aguardando análise", "Eliminados", "Reclassificados", "Contratados"]
                    campos_exist = [c for c in campos if c in df.columns]
                    valores = linha[campos_exist] if campos_exist else pd.Series(dtype=float)
                    fig_pizza = px.pie(values=valores.values, names=valores.index, title=f"{disciplina_escolhida} - {municipio_escolhido_exib}")
                    st.plotly_chart(fig_pizza, use_container_width=True)

                    total_candidatos = linha.get("Total de candidatos", "N/D")
                    convocados = linha.get("Convocados", 0)
                    aguardando = linha.get("Aguardando análise", 0)
                    documentos = linha.get("Documentos analisados", 0)
                    taxa_nao_resposta = ((convocados - (documentos + aguardando)) / convocados * 100) if convocados else 0

                    col1, col2 = st.columns([3,1])
                    with col2:
                        st.markdown(f"**Total de candidatos:** {total_candidatos}")
                        st.markdown(f"**Convocados:** {convocados}")
                        st.markdown(f"**Aguardando análise:** {aguardando}")
                        st.markdown(f"**Documentos analisados:** {documentos}")
                        st.markdown(f"**📉 Taxa de não resposta:** {taxa_nao_resposta:.2f}%")

# ------------------------------------------------------
# 🧭 MENU PRINCIPAL
# ------------------------------------------------------
st.sidebar.title("📂 Menu de Navegação")
pagina = st.sidebar.radio("Selecione o edital:", ["🏠 Página Inicial", "Edital 40/2024", "Edital 42/2024"])

if pagina == "🏠 Página Inicial":
    st.title("📊 Painel de Indicadores")
    st.write("Bem-vindo ao painel de análise dos editais. Use o menu à esquerda para escolher um edital e navegar entre as seções.")
elif pagina == "Edital 40/2024":
    exibir_edital(40)
elif pagina == "Edital 42/2024":
    exibir_edital(42)
