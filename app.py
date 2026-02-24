import streamlit as st
from src.database import connect_db, get_schema, run_query
from src.ai_engine import generate_sql_query

# --- CABEÇALHO ---
st.set_page_config(page_title="SQL Genius", layout="wide")

# --- GERENCIAMENTO DE ESTADO ---
if "db_engine" not in st.session_state:
    st.session_state.db_engine = None
if "db_schema" not in st.session_state:
    st.session_state.db_schema = ""

# --- BARRA LATERAL DE CONFIGURAÇÃO ---
with st.sidebar:
    st.title("🔌 Conexão (GenAI SDK)")
    
    gemini_key = st.text_input("Google API Key", type="password")
    db_uri = st.text_input("Database URI", value="sqlite:///meubanco.db")
    
    if st.button("Conectar ao Banco"):
        if not db_uri:
            st.error("Insira a URI do banco.")
        else:
            try:
                engine = connect_db(db_uri)
                st.session_state.db_engine = engine
                st.session_state.db_schema = get_schema(engine)
                st.success("Conectado!")
                with st.expander("Ver Schema"):
                    st.code(st.session_state.db_schema)
            except Exception as e:
                st.error(f"Erro: {e}")

# --- INTERFACE (PRINCIPAL) ---
st.title("✨ SQL Genius")

if not st.session_state.db_engine:
    st.info("👈 Conecte-se ao banco na barra lateral para começar.")
else:
    question = st.text_area("Pergunta:", placeholder="Ex: Quais clientes fizeram pedidos hoje?")
    
    if st.button("Gerar SQL"):
        if not gemini_key:
            st.warning("Insira a API Key na barra lateral.")
        elif not question:
            st.warning("Escreva uma pergunta.")
        else:
            with st.spinner("Pensando..."):
                sql_result = generate_sql_query(question, st.session_state.db_schema, gemini_key)
                st.code(sql_result, language="sql")
                
                st.subheader("1. Query Gerada")
                
                try:
                    if "Erro" in sql_result and "SELECT" not in sql_result:
                         st.error(sql_result)
                    else:
                        df = run_query(st.session_state.db_engine, sql_result)
                        
                        st.subheader("2. Resultado")
                        if df.empty:
                            st.warning("Consulta sem resultados.")
                        else:
                            st.dataframe(df)
                except Exception as e:
                    st.error(f"Erro ao executar SQL: {e}")