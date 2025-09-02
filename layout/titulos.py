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
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Inscritos", "1.234")
    with col2:
        st.metric("Documentos Recebidos", "1.200")
    with col3:
        st.metric("Documentos Analisados", "1.150")
    with col4:
        st.metric("Deferimentos", "1.100")
with tab2:
    st.write("documentos recebidos, documentos analisados, deferimentos e indeferimentos por Município/Disciplina")
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        with st.container():
            st.markdown("### 🏙️ Inscritos:")
            st.markdown("""
            - **Município A**: 300  
            - **Município B**: 400  
            - **Município C**: 534
            """)
    with col6:
        with st.container():
            st.markdown("### 🏙️ Documentos recebidos:")
            st.markdown("""
            - **Município A**: 280  
            - **Município B**: 370  
            - **Município C**: 500
            """)
    with col7:
        with st.container():
            st.markdown("### 🏙️ Documentos Analisados:")
            st.markdown("""
            - **Município A**: 270  
            - **Município B**: 360  
            - **Município C**: 470
            """)
    with col8:
        with st.container():
            st.markdown("### 🏙️ Deferidos:")
            st.markdown("""
            - **Município A**: 260  
            - **Município B**: 350  
            - **Município C**: 430
            """)
with tab3:
    st.write("quantitativos de convocados para escolha de vaga e contratados por Município/Disciplina")
    col9, col10, col11, col12 = st.columns(4)
    with col9:
        with st.container():
            st.markdown("### 🏙️ Convocados para escolha de vaga:")
            st.markdown("""
            - **Município A**: 150  
            - **Município B**: 200  
            - **Município C**: 250
            """)
    with col10:
        with st.container():
            st.markdown("### 🏙️ Contratados:")
            st.markdown("""
            - **Município A**: 140  
            - **Município B**: 190  
            - **Município C**: 220
            """)
    with col11:
        with st.container():
            st.markdown("### 🏙️ Contratados por Disciplina:")
            st.markdown("""
            - **Matemática**: 100  
            - **Português**: 120  
            - **Ciências**: 110
            """)
    with col12:
        with st.container():
            st.markdown("### 🏙️ Contratados por Nível de Ensino:")
            st.markdown("""
            - **Fundamental**: 180  
            - **Médio**: 150  
            - **Técnico**: 100
            """)
