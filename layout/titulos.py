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
# ABAS PRINCIPAIS DO DASHBOARD
# ------------------------------------------------------------
aba1, aba2, aba3 = st.tabs([
    "📊 Visão Geral",
    "🏙️ Comparativo entre Municípios",
    "🥧 Gráficos de Pizza por Disciplina"
])

# ------------------------------------------------------------
# ABA 1 - VISÃO GERAL
# ------------------------------------------------------------
with aba1:
    st.header("📊 Visão Geral dos Indicadores")
    st.write(
        "Nesta aba, você visualiza o total dos principais indicadores de contratação de professores em designação temporária de **cada município**, "
        "além de uma tabela descritiva gerada automaticamente com o método `describe()`. "
        "Os dados estão organizados por município, por disciplina e para cada uma há: "
        "*Total de candidatos: que são candidatos inscritos no ceertame. "
        "*Aguardando análise: que são documentos recebidos a espera de resultado. "
        "*Eliminados: que são candidatos eliminados. "
        "*Reclassificados: que são candidatos que podem ser chamados novamente. "
        "*Contratados: são os professores que foram efetivamente contratados. "
        "*Documentos analisados: são os documentos enviados pelos candidatos e foram analisados e tem um resultado (ou apto, ou reclassificado, ou eliminado). "
        "*Convocados: candidatos chamados para enviar os documentos para análise."
    )

    # Colunas principais
    colunas_interesse = [
        "Total de candidatos",
        "Aguardando análise",
        "Eliminados",
        "Reclassificados",
        "Contratados",
        "Documentos analisados",
        "Convocados"
    ]

    # Loop pelos municípios
    for municipio, df_mun in dados_municipios.items():
        if not df_mun.empty:
            st.subheader(f"🏙️ {municipio}")

            # --- 1️⃣ TABELA DESCRITIVA DA BASE ---
            st.markdown("#### 📋 Estatísticas descritivas da base de dados")
            try:
                st.dataframe(df_mun[colunas_interesse].describe().T, use_container_width=True)
            except Exception as e:
                st.warning(f"Não foi possível gerar a descrição: {e}")

            # --- 2️⃣ SOMATÓRIO E GRÁFICO DE BARRAS ---
            st.markdown("#### 📊 Totais gerais por indicador")
            soma_municipio = df_mun[colunas_interesse].sum().reset_index()
            soma_municipio.columns = ["Indicador", "Quantidade"]
            st.dataframe(soma_municipio, use_container_width=True)

            # Gráfico usando o Streamlit nativo
            st.bar_chart(
                soma_municipio.set_index("Indicador"),
                y="Quantidade",
                height=400
            )

            st.markdown("---")
# ------------------------------------------------------------
# ABA 2 - GRÁFICOS COMPARATIVOS ENTRE MUNICÍPIOS
# ------------------------------------------------------------
with aba2:
    st.header("📊 Comparativo de Disciplinas entre Municípios")
    st.write(
        "Nesta aba, você pode comparar os indicadores de cada disciplina entre os diferentes municípios. "
        "Cada barra representa a mesma disciplina em municípios distintos."
    )

    colunas_interesse = [
        "Total de candidatos",
        "Convocados",
        "Documentos analisados",
        "Aguardando análise",
        "Reclassificados",
        "Eliminados",
        "Contratados"

    ]

    # 1️⃣ Unir todas as bases de municípios em um único DataFrame
    dados_validos = []
    for municipio, df_mun in dados_municipios.items():
        if not df_mun.empty:
            df_temp = df_mun.copy()
            df_temp["Município"] = municipio  # adiciona a identificação
            dados_validos.append(df_temp)

    # Verifica se há mais de uma base
    if len(dados_validos) < 2:
        st.warning("⚠️ É necessário ter ao menos duas bases de municípios para gerar comparativos.")
    else:
        df_comparativo = pd.concat(dados_validos, ignore_index=True)

        # 2️⃣ Escolher indicador e disciplina para comparar
        indicador_escolhido = st.selectbox(
            "Selecione o indicador para comparar entre municípios:",
            colunas_interesse
        )

        disciplinas_disponiveis = df_comparativo["Disciplina"].unique()
        disciplina_escolhida = st.selectbox(
            "Selecione a disciplina para comparação:",
            sorted(disciplinas_disponiveis)
        )

        # 3️⃣ Filtrar e plotar o gráfico
        df_filtrado = df_comparativo[df_comparativo["Disciplina"] == disciplina_escolhida]

        if not df_filtrado.empty:
            fig = px.bar(
                df_filtrado,
                x="Município",
                y=indicador_escolhido,
                color="Município",
                title=f"{indicador_escolhido} - {disciplina_escolhida}",
                text=indicador_escolhido
            )
            fig.update_layout(yaxis_title="Quantidade", xaxis_title="Município")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados disponíveis para esta disciplina nos municípios selecionados.")
# ------------------------------------------------------------
# ABA 3 - GRÁFICOS DE PIZZA POR MUNICÍPIO E DISCIPLINA
# ------------------------------------------------------------
with aba3:
    st.header("🥧 Gráficos de Pizza - Indicadores por Disciplina e Município")
    st.write("Visualização detalhada dos indicadores por disciplina, com totais ao lado dos gráficos.")

    for m, df_municipio in dados_municipios.items():
        if not df_municipio.empty:
            st.subheader(f"🏫 {m}")

            for _, linha in df_municipio.iterrows():
                disciplina = linha["Disciplina"]

                # Retira "Documentos analisados" da pizza
                valores_pizza = linha[["Aguardando análise", "Contratados","Eliminados", "Reclassificados"]]

                # Cria o gráfico de pizza
                fig_pizza = px.pie(
                    values=valores_pizza.values,
                    names=valores_pizza.index,
                    title=f"{disciplina} - {m}"
                )

                # Mostra gráfico e totais lado a lado
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.plotly_chart(fig_pizza, use_container_width=True)

                with col2:
                    st.markdown(f"""
                    **📘 Disciplina:** {disciplina}  
                    **👥 Total de candidatos:** {linha['Total de candidatos']}  
                    **📄 Documentos analisados:** {linha['Documentos analisados']}  
                    **✅ Convocados:** {linha['Convocados']}
                    """)

