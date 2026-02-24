from pydantic import BaseModel, Field, field_validator

class DatabaseParameters(BaseModel):
    dialect: str
    database: str
    host: str = Field(..., description="O endereço do servidor")
    user: str | None = None
    password: str | None = None

    @field_validator('dialect')
    @classmethod
    def validate_dialect(cls, v: str) -> str:
        validos = ['postgresql', 'mysql', 'sqlite', 'oracle']
        if v.lower() not in validos:
            raise ValueError(
                f"Dialeto '{v}' não suportado. Escolha entre: {validos}")
        return v.lower()

    def get_uri(self) -> str:
        if self.dialect == "sqlite":
            return f"sqlite:///{self.database}"
        return f"{self.dialect}://{self.user}:{self.password}@{self.host}/{self.database}"
