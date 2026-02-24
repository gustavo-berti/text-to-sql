from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
import pandas as pd

class DatabaseService:
    def __init__(self):
        self._engine: Engine | None = None
        self._params: DatabaseParameters | None = None
        self._schema_cache: str | None = None

    def connect(self, params: DatabaseParameters):
        try:
            new_engine = create_engine(params.get_uri())
            with new_engine.connect() as conn:
                pass
            self._engine = new_engine
            self._params = params
            self._schema_cache = None  
            return True
        except Exception as e:
            raise ConnectionError(f"Falha ao conectar no banco: {e}")

    def get_schema(self) -> str:
        if not self._engine:
            return "Nenhum banco conectado."

        if self._schema_cache:
            return self._schema_cache

        inspector = inspect(self._engine)
        schema_text = ""
        for table_name in inspector.get_table_names():
            schema_text += f"\nTabela: {table_name}\n"
            for col in inspector.get_columns(table_name):
                schema_text += f" - {col['name']} ({col['type']})\n"

        self._schema_cache = schema_text
        return schema_text

    def execute_query(self, sql: str) -> pd.DataFrame:
        if not self._engine:
            raise RuntimeError("Conecte-se a um banco primeiro.")

        with self._engine.connect() as conn:
            return pd.read_sql(text(sql), conn)

    @property
    def is_connected(self) -> bool:
        return self._engine is not None
