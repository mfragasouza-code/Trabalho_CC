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
# Definição das seções (abas)
SECTION_NAMES = ["📈 Visão Geral", "📊 Gráficos Comparativos", "🥧 Gráficos Município/Disciplina"]

st.set_page_config(
    page_title="Indicadores - Editais 40 e 43/2024", # CORRIGIDO: 42 -> 43
    layout="wide",
    initial_sidebar_state="expanded"
)

# TÍTULO PRINCIPAL
st.title("📊 Indicadores dos Editais 40/2024 e 43/2024 - SRE Carapina") # CORRIGIDO: 42 -> 43
st.markdown("""
Análise comparativa por **município** e **disciplina**, com base nos indicadores dos processos seletivos.
Por *Mirella Fraga*
**Obs.:** Base de dados temporária e unificada enquanto o MVP é desenvolvido.
""")

# ------------------------------------------------------------
# FUNÇÃO PARA CARREGAR OS DADOS
# ------------------------------------------------------------
# Nota: Para rodar, você deve ter os arquivos .xlsx no mesmo diretório.
def carregar_dados():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    arquivos = {
        "Vitória 40": os.path.join(BASE_DIR, "vitoria_40.xlsx"),
        "Serra 40": os.path.join(BASE_DIR, "serra_40.xlsx"),
        "Fundão 40": os.path.join(BASE_DIR, "fundao_40.xlsx"),
        "Santa Teresa 40": os.path.join(BASE_DIR, "santa_teresa_40.xlsx"),
        # CORRIGIDO: Referências a Edital 42 alteradas para 43
        "Vitória 43": os.path.join(BASE_DIR, "vitoria_43.xlsx"),
        "Serra 43": os.path.join(BASE_DIR, "serra_43.xlsx"),
        "Fundão 43": os.path.join(BASE_DIR, "fundao_43.xlsx"),
        "Santa Teresa 43": os.path.join(BASE_DIR, "santa_teresa_43.xlsx"),
    }

    dados = {}
    for nome, caminho in arquivos.items():
        if os.path.exists(caminho):
            try:
                dados[nome] = pd.read_excel(caminho)
            except Exception as e:
                st.error(f"Erro ao ler o arquivo {caminho}: {e}")
        else:
            print(f"⚠️ Arquivo não encontrado: {caminho}")
    return dados

# ------------------------------------------------------------
# CARREGAMENTO DOS DADOS
# ------------------------------------------------------------
dados_municipios = carregar_dados()

# Inicializa o estado de subpagina, se não existir OU se o valor for inválido, volta para o padrão.
if ('subpagina_selecionada' not in st.session_state) or (st.session_state.subpagina_selecionada not in SECTION_NAMES): 
    st.session_state.subpagina_selecionada = SECTION_NAMES[0]

# ------------------------------------------------------------
# MENU LATERAL HIERÁRQUICO E COLAPSÁVEL
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("## 📁 Menu de Navegação")
    with st.expander("🌍 Selecione o Edital", expanded=True):
        menu_principal = st.radio(
            "Escolha o edital:",
            # CORRIGIDO: Edital 42/2024 alterado para 43/2024
            ("Página Inicial", "Edital 40/2024", "Edital 43/2024"),
            key="menu_principal"
        )

    # Submenus (apenas aparecem se um Edital estiver selecionado)
    if "40" in menu_principal:
        numero_edital = 40
    # CORRIGIDO: Checagem para "43" e atribuição do número 43
    elif "43" in menu_principal: 
        numero_edital = 43
    else:
        numero_edital = None

    if numero_edital:
        with st.expander(f"📘 Edital {numero_edital}/2024 - Seções", expanded=True):
            # O valor selecionado do rádio é salvo diretamente no st.session_state.subpagina_selecionada
            st.radio(
                "Navegue entre as seções:",
                SECTION_NAMES,
                key="subpagina_selecionada", # Usa a chave do session_state diretamente
                # Define o índice com base no valor atual do session_state
                # Adicionada proteção extra: se o valor não estiver na lista, retorna 0 (Visão Geral)
                index=SECTION_NAMES.index(st.session_state.subpagina_selecionada) if st.session_state.subpagina_selecionada in SECTION_NAMES else 0
            )

# ------------------------------------------------------------
# PÁGINA INICIAL
# ------------------------------------------------------------
if menu_principal == "Página Inicial":
    st.header("🏠 Página Inicial")
    st.markdown("""
    Bem-vindo ao **Painel Interativo de Indicadores dos Editais 40/2024 e 43/2024** da SRE Carapina. 
    Aqui você poderá visualizar:
    - 📈 Indicadores gerais por município;
    - 📊 Gráficos comparativos por disciplina;
    - 🥧 Distribuições detalhadas por município e disciplina.

    Use o menu lateral para navegar entre os editais e suas seções.
    """)

# ------------------------------------------------------------
# FUNÇÃO PARA EXIBIR CADA EDITAL
# ------------------------------------------------------------
elif numero_edital:
    st.header(f"📘 Indicadores - {menu_principal}")
    st.markdown(f"Análise dos indicadores do **{menu_principal}**, por município e disciplina.")

    # Filtrar dados do edital
    dados_edital = {k: v for k, v in dados_municipios.items() if k.endswith(str(numero_edital))}

    if not dados_edital:
        st.warning("⚠️ Nenhum dado encontrado. Verifique os arquivos Excel.")
    else:
        # 1. Obter a aba a ser ativada do estado da sessão de forma segura
        # Usa .get() com valor padrão para evitar erro se 'subpagina_selecionada' não estiver pronta
        selected_section_name = st.session_state.get('subpagina_selecionada', SECTION_NAMES[0])
        
        # 2. Calcular o índice da aba a ser ativada (sincronização Sidebar -> Tab)
        # Proteção: Se a seção selecionada for desconhecida, assume 0 (Visão Geral)
        try:
            selected_index = SECTION_NAMES.index(selected_section_name)
        except ValueError:
            selected_index = 0

        # 3. Criar as abas, forçando a seleção pelo índice do menu lateral
        # Se houver um erro de tipo, force o índice 0 para evitar quebra
        try:
             abas = st.tabs(SECTION_NAMES, index=selected_index)
        except Exception:
             abas = st.tabs(SECTION_NAMES, index=0)
             
        abas_dict = dict(zip(SECTION_NAMES, abas))

        # ------------------------------------------------------------
        # VISÃO GERAL (Índice 0)
        # ------------------------------------------------------------
        with abas_dict[SECTION_NAMES[0]]:
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
        # GRÁFICOS COMPARATIVOS (Índice 1)
        # ------------------------------------------------------------
        with abas_dict[SECTION_NAMES[1]]:
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
        # GRÁFICOS MUNICÍPIO / DISCIPLINA (Índice 2)
        # ------------------------------------------------------------
        with abas_dict[SECTION_NAMES[2]]:
            st.subheader("🥧 Indicadores por Disciplina e Município")

            municipios_disponiveis = list(dados_edital.keys())
            municipio_escolhido = st.selectbox(
                "Selecione o município:",
                municipios_disponiveis,
                key=f"select_municipio_pizza_{numero_edital}"
            )

            if municipio_escolhido:
                df = dados_edital[municipio_escolhido]
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
                        title=f"{disciplina_escolhida} - {municipio_escolhido} ({numero_edital}/2024)"
                    )

                    total_candidatos = linha["Total de candidatos"]
                    convocados = linha["Convocados"]
                    aguardando = linha["Aguardando análise"]
                    documentos = linha["Documentos analisados"]

                    taxa_nao_resposta = 0
                    if convocados > 0:
                        # Corrigida a lógica: Taxa de não resposta = (Convocados - Documentos Recebidos) / Convocados
                        documentos_recebidos = linha["Aguardando análise"] + linha["Eliminados"] + linha["Reclassificados"] + linha["Contratados"]
                        taxa_nao_resposta = ((convocados - documentos_recebidos) / convocados) * 100

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.plotly_chart(fig_pizza, use_container_width=True)
                    with col2:
                        st.markdown(f"**Total de candidatos:** {total_candidatos}")
                        st.markdown(f"**Convocados:** {convocados}")
                        st.markdown(f"**Aguardando análise:** {aguardando}")
                        st.markdown(f"**Documentos analisados:** {documentos}")
                        st.markdown(f"**📉 Taxa de não resposta:** {taxa_nao_resposta:.2f}%")
