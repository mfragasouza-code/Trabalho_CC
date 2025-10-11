import streamlit as st
import plotly.express as px
import pandas as pd

# ------------------------------------------------------------
# CONFIGURAÇÕES GERAIS DO APP
# ------------------------------------------------------------
st.set_page_config(page_title="Painel de Análise dos Editais", layout="wide")

st.title("📊 Painel de Acompanhamento dos Editais por Município")

# Definindo as colunas de interesse para validação e uso
COLUNAS_INTERESSE = [
    "Disciplina",
    "Total de candidatos",
    "Aguardando análise",
    "Eliminados",
    "Reclassificados",
    "Contratados",
    "Documentos analisados",
    "Convocados"
]

# ------------------------------------------------------------
# FUNÇÃO PARA LER AS BASES DE DADOS E APLICAR CACHE
# ------------------------------------------------------------
@st.cache_data
def carregar_dados():
    # Caminhos dos arquivos de exemplo.
    # OBSERVAÇÃO: Estes arquivos (vitoria.xlsx, etc.) precisam estar na mesma pasta
    # do script Python para que o código funcione.
    
    # Criando um dicionário de caminhos (ideal para projetos maiores)
    caminhos = {
        "Vitória": "vitoria.xlsx",
        "Serra": "serra.xlsx",
        "Fundão": "fundao.xlsx",
        "Santa Teresa": "santa_teresa.xlsx"
    }
    
    dados_municipios = {}
    
    for municipio, caminho in caminhos.items():
        try:
            df = pd.read_excel(caminho)
            
            # 1. Verificar se a coluna 'Disciplina' existe
            if "Disciplina" not in df.columns:
                st.error(f"⚠️ O arquivo de **{municipio}** não possui a coluna 'Disciplina'. Dados não carregados.")
                continue

            # 2. Verificar se todas as colunas numéricas necessárias existem
            colunas_numericas_faltantes = [
                col for col in COLUNAS_INTERESSE if col != "Disciplina" and col not in df.columns
            ]
            
            if colunas_numericas_faltantes:
                st.warning(f"🚨 O arquivo de **{municipio}** está faltando as colunas: {', '.join(colunas_numericas_faltantes)}. Ignorando...")
                # Cria um DataFrame vazio para evitar erros
                df = pd.DataFrame() 
            else:
                # Se tudo estiver ok, armazena no dicionário
                dados_municipios[municipio] = df
                
        except FileNotFoundError:
            st.error(f"🚫 Arquivo **{caminho}** não encontrado para **{municipio}**. Verifique o caminho.")
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados de {municipio}: {e}")
            
    return dados_municipios

dados_municipios = carregar_dados()

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
    
    # Lista de indicadores melhor formatada usando st.markdown
    st.markdown("""
        Nesta aba, você visualiza o total dos principais indicadores de contratação de professores 
        em designação temporária de **cada município**, além de uma tabela descritiva gerada 
        automaticamente com o método `describe()`. 
        
        Os dados estão organizados por município, por disciplina e para cada uma há:
        * **Total de candidatos:** inscritos no certame.
        * **Aguardando análise:** documentos recebidos à espera de resultado.
        * **Eliminados:** candidatos eliminados.
        * **Reclassificados:** candidatos que podem ser chamados novamente.
        * **Contratados:** professores que foram efetivamente contratados.
        * **Documentos analisados:** documentos enviados pelos candidatos que foram analisados e têm um resultado (apto, reclassificado ou eliminado).
        * **Convocados:** candidatos chamados para enviar os documentos para análise.
    """)

    # Filtrando apenas as colunas numéricas que serão usadas para cálculo/gráfico
    colunas_numericas = [col for col in COLUNAS_INTERESSE if col != "Disciplina"]

    # Loop pelos municípios
    for municipio, df_mun in dados_municipios.items():
        if not df_mun.empty:
            st.subheader(f"🏙️ {municipio}")

            # --- 1️⃣ TABELA DESCRITIVA DA BASE ---
            st.markdown("#### 📋 Estatísticas descritivas da base de dados")
            try:
                # Garante que só está descrevendo as colunas numéricas válidas
                st.dataframe(df_mun[colunas_numericas].describe().T, use_container_width=True)
            except Exception as e:
                st.warning(f"Não foi possível gerar a descrição para {municipio}: {e}")

            # --- 2️⃣ SOMATÓRIO E GRÁFICO DE BARRAS ---
            st.markdown("#### 📊 Totais gerais por indicador")
            
            # Cria a soma e limpa o índice
            soma_municipio = df_mun[colunas_numericas].sum().reset_index()
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

    # 1️⃣ Unir todas as bases de municípios em um único DataFrame
    dados_validos = []
    for municipio, df_mun in dados_municipios.items():
        if not df_mun.empty:
            df_temp = df_mun.copy()
            df_temp["Município"] = municipio  # adiciona a identificação
            dados_validos.append(df_temp)

    # Verifica se há bases para comparar
    if len(dados_validos) < 2:
        st.warning("⚠️ É necessário ter ao menos duas bases de municípios válidas para gerar comparativos.")
    elif not dados_validos:
        st.error("Nenhum dado válido encontrado para comparação.")
    else:
        df_comparativo = pd.concat(dados_validos, ignore_index=True)
        colunas_numericas = [col for col in COLUNAS_INTERESSE if col != "Disciplina"]

        # 2️⃣ Escolher indicador e disciplina para comparar
        indicador_escolhido = st.selectbox(
            "Selecione o indicador para comparar entre municípios:",
            colunas_numericas # Usando apenas as colunas numéricas
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
            
            colunas_pizza = ["Aguardando análise", "Contratados", "Eliminados", "Reclassificados"]

            for _, linha in df_municipio.iterrows():
                disciplina = linha["Disciplina"]

                # Retira "Documentos analisados" e "Total de candidatos" da pizza, 
                # focando apenas no status final dos candidatos (Aguardando/Contratados/Reclassificados/Eliminados)
                try:
                    valores_pizza = linha[colunas_pizza]

                    # Cria o gráfico de pizza
                    fig_pizza = px.pie(
                        values=valores_pizza.values,
                        names=valores_pizza.index,
                        title=f"{disciplina} - {m}"
                    )
                    fig_pizza.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))

                    # Mostra gráfico e totais lado a lado
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.plotly_chart(fig_pizza, use_container_width=True)

                    with col2:
                        st.markdown(f"""
                        **📘 Disciplina:** {disciplina}  
                        **👥 Total de candidatos:** {linha.get('Total de candidatos', 'N/D')}  
                        **📄 Documentos analisados:** {linha.get('Documentos analisados', 'N/D')}  
                        **✅ Convocados:** {linha.get('Convocados', 'N/D')}
                        """)
                    st.markdown("---")
                except KeyError as e:
                    st.warning(f"Coluna faltando na aba 3 para {municipio} e disciplina {disciplina}: {e}. Verifique as colunas {colunas_pizza}.")
                except Exception as e:
                    st.error(f"Erro inesperado na aba 3 para {municipio} e disciplina {disciplina}: {e}")
