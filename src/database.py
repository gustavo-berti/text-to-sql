from sqlalchemy import create_engine, inspect, text
import pandas as pd

def connect_db(uri):
    try:
        engine = create_engine(uri)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")) # Teste rápido de conexão
        return engine
    except Exception as e:
        raise Exception(f"Erro ao conectar ao banco: {e}")
    
def get_schema(engine):
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
        raise Exception(f"Erro ao ler schema: {e}")
    
def run_query(engine, query):
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn)
    except Exception as e:
        raise Exception(f"Erro ao executar query: {e}")