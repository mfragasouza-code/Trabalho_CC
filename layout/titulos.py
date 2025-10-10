import streamlit as st
import plotly.express as px
import pandas as pd

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
# CRIAÇÃO DAS ABAS
# ------------------------------------------------------------
aba_geral, aba_barras, aba_pizza = st.tabs([
    "📊 Visão Geral",
    "🏙️ Gráficos Comparativos entre Municípios",
    "🥧 Gráficos de Pizza por Município e Disciplina"
])

# ------------------------------------------------------------
# 📊 ABA 1 — VISÃO GERAL
# ------------------------------------------------------------
with aba_geral:
    st.header("📊 Visão Geral das Disciplinas por Município")

    for m, df in dados_municipios.items():
        if not df.empty:
            st.subheader(f"📍 {m}")
            
            # Padroniza os nomes das colunas
            df.columns = df.columns.str.strip().str.lower()

            # Estatísticas básicas por disciplina
            st.dataframe(df.describe(include='all'))

            # Gráfico de barras por disciplina
            col_disciplina = next((c for c in df.columns if "disciplina" in c), None)
            col_total = next((c for c in df.columns if "total" in c and "candidato" in c), None)

            if col_disciplina and col_total:
                fig_total = px.bar(
                    df,
                    x=col_disciplina,
                    y=col_total,
                    title=f"Total de Candidatos por Disciplina - {m}",
                    labels={"x": "Disciplina", "y": "Quantidade"}
                )
                st.plotly_chart(fig_total, use_container_width=True)

# ------------------------------------------------------------
# 🏙️ ABA 2 — GRÁFICOS DE BARRAS COMPARATIVOS
# ------------------------------------------------------------
with aba_barras:
    st.header("🏙️ Comparativo de Disciplinas entre Municípios")

    # Criação de base consolidada
    dfs_renomeados = []
    for m, df in dados_municipios.items():
        if not df.empty:
            df = df.copy()
            df.columns = df.columns.str.strip().str.lower()
            col_disciplina = next((c for c in df.columns if "disciplina" in c), None)
            col_total = next((c for c in df.columns if "total" in c and "candidato" in c), None)
            if col_disciplina and col_total:
                df["município"] = m
                dfs_renomeados.append(df[[col_disciplina, col_total, "município"]])

    if dfs_renomeados:
        df_comparativo = pd.concat(dfs_renomeados)
        fig_comp = px.bar(
            df_comparativo,
            x="disciplina",
            y=col_total,
            color="município",
            barmode="group",
            title="Comparativo de Candidatos por Disciplina entre Municípios",
            labels={"disciplina": "Disciplina", "quantidade": "Quantidade"}
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# ------------------------------------------------------------
# 🥧 ABA 3 — GRÁFICOS DE PIZZA
# ------------------------------------------------------------
with aba_pizza:
    st.header("🥧 Gráficos de Pizza - Indicadores por Disciplina e Município")

    for m, df in dados_municipios.items():
        if not df.empty:
            st.subheader(f"{m}")
            df.columns = df.columns.str.strip().str.lower()

            col_disciplina = next((c for c in df.columns if "disciplina" in c), None)
            col_total = next((c for c in df.columns if "total" in c and "candidato" in c), None)

            for _, linha in df.iterrows():
                disciplina = linha[col_disciplina]
                total_candidatos = linha[col_total] if col_total in df.columns else None

                # Seleciona apenas os indicadores
                colunas_indicadores = [c for c in df.columns if c not in [col_disciplina, col_total, "município"]]
                valores = linha[colunas_indicadores]

                # Criação do gráfico de pizza
                fig_pizza = px.pie(
                    values=valores.values,
                    names=[c.title() for c in colunas_indicadores],
                    title=f"{disciplina} - {m}"
                )

                # Exibição lado a lado
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.plotly_chart(fig_pizza, use_container_width=True)
                with col2:
                    if total_candidatos is not None:
                        st.markdown(f"""
                        **Total de Candidatos:**  
                        <span style='font-size:1.5em; color:#2c5282; font-weight:bold;'>{int(total_candidatos)}</span>
                        """, unsafe_allow_html=True)
