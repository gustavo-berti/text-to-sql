from abc import ABC, abstractmethod

class LLMService(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = self._create_client()

    @abstractmethod
    def _create_client(self):
        pass

    @abstractmethod
    def _call_model(self, prompt: str) -> str:
        pass

    def generate_sql_query(self, question: str, schema: str, db_type: str) -> str:
        try:
            bd_type = db_type.upper() if db_type else "GENERIC SQL"
            prompt = self._build_prompt(question, schema, bd_type)
            response_text = self._call_model(prompt)

            if not response_text:
                raise Exception("Erro: A IA não retornou texto.")
            return self._clean_response(response_text)

        except Exception as e:
            raise Exception(f"Erro ao gerar SQL: {e}")

    def _build_prompt(self, question: str, schema: str, db_type: str) -> str:
        return f"""
        Você é um especialista em SQL. Converta a pergunta do usuário em uma consulta SQL válida baseada no schema fornecido e no tipo de banco de dados informado.

        SCHEMA DO BANCO DE DADOS:
        {schema}

        TIPO DE BANCO DE DADOS
        {db_type}
        
        PERGUNTA DO USUÁRIO:
        "{question}"
        
        REGRAS ESTRITAS:
        1. Retorne APENAS o código SQL puro.
        2. NÃO use markdown (sem ```sql ou ```). Apenas o texto da query.
        3. Não invente colunas, caso seja informada uma coluna inesistente, retorne uma mensagem de aviso.
        4. Não responda com outras operações além de SELECT.
        5. Caso seja identificado um pedido não condizente com SELECT, retorne uma mensagem de erro.
        6. Caso haja nomes de colunas iguais em 2 tabelas de uma query, utilize apelidos 'AS' para evitar confusão.
        """
    
    def _clean_response(self, text: str) -> str:
        return text.replace("```sql", "").replace("```", "").strip()
    
    @abstractmethod
    def analyze_microservices(self, schema: str) -> str:
        pass    
    

from google import genai


class GeminiLLMService(LLMService):

    def _create_client(self):
        return genai.Client(api_key=self.api_key)

    def _call_model(self, prompt: str) -> str:
        response = self.client.models.generate_content( # type: ignore
            model="gemini-3-flash-preview",
            contents=prompt
        )

        return response.text if response.text else None # type: ignore
    
    def explain_query(self, query: str) -> str:
        try:
            prompt = f"Explique de forma didática e enxuta o que a seguinte query SQL faz, passo a passo:\n{query}"
            response_text = self._call_model(prompt)

            if not response_text:
                raise Exception("Erro: A IA não retornou texto.")
            return response_text.strip()
        except Exception as e:
            raise Exception(f"Erro ao explicar SQL: {e}")
    
    def explain_results(self, question: str, results: str) -> str:
        try:
            prompt = f"""
            Pergunta original: {question}
            Dados retornados: {results}
            
            Explique o que esses dados significam em relação à pergunta do usuário.
            Seja breve e didático, destacando insights importantes. Evite repetir a pergunta ou os dados, foque na interpretação. 
            """
            response_text = self._call_model(prompt)

            if not response_text:
                raise Exception("Erro: A IA não retornou texto.")
            return response_text.strip()
        except Exception as e:
            raise Exception(f"Erro ao explicar resultados: {e}")
        
    def analyze_microservices(self, schema: str) -> str:
        try:
            prompt = f"""
            Você é um Arquiteto de Software Sênior especialista em migração de sistemas monolíticos para microsserviços (Domain-Driven Design).
            Abaixo está o schema do banco de dados relacional que representa o sistema monolítico atual:
            
            SCHEMA DO BANCO DE DADOS:
            {schema}
            
            Sua tarefa:
            Com base nas tabelas e relacionamentos apresentados, sugira uma divisão lógica deste sistema em Microsserviços (Bounded Contexts).
            Para cada microsserviço sugerido, explique:
            1. O nome do Microsserviço.
            2. Quais tabelas (entidades) pertenceriam a ele.
            3. Qual a justificativa técnica para essa divisão.
            
            Responda de forma clara, profissional e bem formatada em Markdown.
            """
            response_text = self._call_model(prompt)

            if not response_text:
                raise Exception("Erro: A IA não retornou texto.")
            return response_text.strip()
        except Exception as e:
            raise Exception(f"Erro ao gerar análise de microsserviços: {e}")