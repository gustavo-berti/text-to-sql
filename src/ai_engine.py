from google import genai

def generate_sql_query(question, schema, api_key):
    try:
        client = genai.Client(api_key=api_key)
        
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

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        
        if response.text:
            clean_sql = response.text.replace("```sql", "").replace("```", "").strip()
            return clean_sql
        else:
            raise Exception("Erro: A IA não retornou texto.")
    except Exception as e:
        raise Exception(f"Erro ao gerar SQL: {e}")