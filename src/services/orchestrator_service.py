class OrchestratorService:
    def __init__(self, llm_service, db_service, max_retries=2):
        self.llm_service = llm_service
        self.db_service = db_service
        self.max_retries = max_retries

    def run(self, question: str, schema: str, db_type: str):
        attempts = 0
        last_error = None
        last_query = None

        while attempts <= self.max_retries:
            if attempts == 0:
                query = self.llm_service.generate_sql_query(question, schema, db_type)
            else:
                query = self.llm_service.retry_sql_query_generate(
                    question=question,
                    schema=schema,
                    db_type=db_type,
                    last_query=last_query,
                    last_error=last_error
                )

            try:
                result = self.db_service.execute_query(query)
                return {
                    "success": True,
                    "query": query,
                    "result": result,
                    "attempts": attempts
                }

            except Exception as e:
                last_error = str(e)
                last_query = query
                attempts += 1

        return {
            "success": False,
            "query": last_query,
            "error": last_error,
            "attempts": attempts
        }