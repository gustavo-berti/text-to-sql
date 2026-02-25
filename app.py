import streamlit as st
from src.ai_engine import generate_sql_query
from src.models.database_parameters import DatabaseParameters
from src.services.database_service import DatabaseService

# --- CABEÇALHO ---
st.set_page_config(page_title="SQL Genius", layout="wide")

# --- GERENCIAMENTO DE ESTADO ---
if "db_service" not in st.session_state:
    st.session_state.db_service = DatabaseService()

# --- BARRA LATERAL DE CONFIGURAÇÃO ---
with st.sidebar:
    st.title("🔌 Conexão")

    db_type = st.selectbox("Banco", ["postgresql", "mysql", "oracle"])
    host = st.text_input("Host", value="localhost")
    database = st.text_input("Nome do Banco")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    gemini_key = st.text_input("Google API Key", type="password")

    if st.button("Conectar"):
        try:
            config = {
                "host": host,
                "database": database,
                "user": user,
                "password": password
            }

            params = DatabaseParameters.make(db_type, **config)

            if st.session_state.db_service.connect(params):
                st.success(f"Conectado ao {params.get_dialect_name()}!")

                with st.expander("Ver Schema"):
                    st.code(st.session_state.db_service.get_schema())

        except Exception as e:
            st.error(f"Erro na conexão: {e}")

# --- INTERFACE (PRINCIPAL) ---
st.title("✨ SQL Genius")

# Verificamos se o serviço está conectado através da property que criamos
if not st.session_state.db_service.is_connected:
    st.info("👈 Conecte-se ao banco na barra lateral para começar.")
else:
    question = st.text_area("Sua pergunta:", placeholder="Ex: Qual o total de vendas por mês?")
    
    if st.button("Gerar e Executar"):
        if not gemini_key:
            st.warning("Insira a API Key.")
        elif not question:
            st.warning("Faça uma pergunta.")
        else:
            with st.spinner("IA processando..."):
                current_schema = st.session_state.db_service.get_schema()
                current_dialect = st.session_state.db_service._params.get_dialect_name()
                
                sql_result = generate_sql_query(question, current_schema, gemini_key, current_dialect)
                
                st.subheader("Query Gerada")
                st.code(sql_result, language="sql")
                
                # 3. Executamos via Service
                try:
                    df = st.session_state.db_service.execute_query(sql_result)
                    
                    st.subheader("Resultado")
                    if df.empty:
                        st.warning("Nenhum dado encontrado.")
                    else:
                        st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao executar no banco: {e}")