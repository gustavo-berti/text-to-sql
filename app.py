import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from google import genai  # Nova importação da SDK v1.0+

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SQL Genius (New GenAI SDK)", layout="wide")

# --- GERENCIAMENTO DE ESTADO ---
if "db_engine" not in st.session_state:
    st.session_state.db_engine = None
if "db_schema" not in st.session_state:
    st.session_state.db_schema = ""

# --- FUNÇÕES ---

def get_database_schema(engine):
    """Extrai automaticamente a estrutura do banco de dados."""
    inspector = inspect(engine)
    schema_text = ""
    try:
        for table_name in inspector.get_table_names():
            schema_text += f"\nTabela: {table_name}\n"
            columns = inspector.get_columns(table_name)
            for col in columns:
                schema_text += f" - {col['name']} ({col['type']})\n"
        return schema_text
    except Exception as e:
        return f"Erro ao ler schema: {e}"

def generate_sql_query(question, schema, api_key):
    """Gera SQL usando a nova SDK 'google-genai'."""
    
    try:
        # 1. Instancia o Cliente (Nova Sintaxe)
        client = genai.Client(api_key=api_key)
        
        # 2. Engenharia de Prompt
        prompt = f"""
        Você é um especialista em SQL. Converta a pergunta do usuário em uma consulta SQL válida baseada no schema fornecido.

        SCHEMA DO BANCO DE DADOS:
        {schema}
        
        PERGUNTA DO USUÁRIO:
        "{question}"
        
        REGRAS ESTRITAS:
        1. Retorne APENAS o código SQL puro.
        2. NÃO use markdown (sem ```sql ou ```). Apenas o texto da query.
        3. Não invente colunas.
        """

        # 3. Chamada de Geração (Nova Sintaxe: client.models.generate_content)
        response = client.models.generate_content(
            model="gemini-3-flash-preview", # Usando o modelo mais recente e rápido
            contents=prompt
        )
        
        # Limpeza de segurança
        if response.text:
            clean_sql = response.text.replace("```sql", "").replace("```", "").strip()
            return clean_sql
        else:
            return "Erro: A IA não retornou texto."
            
    except Exception as e:
        return f"Erro na API GenAI: {e}"

# --- INTERFACE (SIDEBAR) ---
with st.sidebar:
    st.title("🔌 Conexão (GenAI SDK)")
    
    gemini_key = st.text_input("Google API Key", type="password")
    db_uri = st.text_input("Database URI", value="sqlite:///meubanco.db")
    
    if st.button("Conectar ao Banco"):
        if not db_uri:
            st.error("Insira a URI do banco.")
        else:
            try:
                engine = create_engine(db_uri)
                # Teste rápido de conexão
                with engine.connect() as conn:
                    pass 
                st.session_state.db_engine = engine
                st.session_state.db_schema = get_database_schema(engine)
                st.success("Conectado! Schema extraído.")
                with st.expander("Ver Schema"):
                    st.code(st.session_state.db_schema)
            except Exception as e:
                st.error(f"Erro: {e}")

# --- INTERFACE (PRINCIPAL) ---
st.title("✨ SQL Genius")
st.caption("Powered by Google GenAI SDK (v1.0+)")

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
            with st.spinner("Consultando Gemini 2.0 Flash..."):
                sql_result = generate_sql_query(question, st.session_state.db_schema, gemini_key)
                
                st.subheader("1. Query Gerada")
                st.code(sql_result, language="sql")
                
                # Executar no Banco
                try:
                    # Verifica se o SQL não é uma mensagem de erro da função anterior
                    if "Erro" in sql_result and "SELECT" not in sql_result:
                         st.error(sql_result)
                    else:
                        with st.session_state.db_engine.connect() as conn:
                            df = pd.read_sql(text(sql_result), conn)
                        
                        st.subheader("2. Resultado")
                        if df.empty:
                            st.warning("Consulta sem resultados.")
                        else:
                            st.dataframe(df)
                except Exception as e:
                    st.error(f"Erro ao executar SQL: {e}")