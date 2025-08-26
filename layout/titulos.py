import streamlit as st

st.title("Tema: Monitoramento da Contratação de Servidores em Designação Temporária da SRE Carapina")
st.header("Nome: Mirella Fraga Souza",anchor="home")

st.write("A partir da escolha do edital, o usuário monitorar as listas de classificação para contratação de professores.")
st.write("Base de Dados: base da dados interna da SRE")

st.sidebar.title("📂 Editais")
opcao = st.sidebar.radio("Escolha o edital:", ["🏠 Edital 40/2024", "📊 Edital 42/2024"])

import streamlit as st

tab1, tab2, tab3 = st.tabs(["📊 Monitoramento Geral", "🌎 Análises por Município/Disciplina", "📈 Contratações por Município/Disciplina"])

with tab1:
    st.write("informações gerais, como quantidades de inscritos, documentos recebidos, documentos analisados")
with tab2:
    st.write("documentos recebidos, documentos analisados, deferimentos e indeferimentos por Município/Disciplina")
with tab3:
    st.write("quantitativos de convocados para escolha de vaga e contratados por Município/Disciplina")

