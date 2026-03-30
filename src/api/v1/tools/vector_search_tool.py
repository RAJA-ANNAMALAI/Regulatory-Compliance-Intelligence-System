from langchain_core.tools import tool
from src.api.v1.services.query_service import vector_search

@tool
def semantic_search_tool(query: str,k: int):
    """
    Use this tool for natural language questions.
    Ideal for understanding context, feelings, or broad HR topics.
    """
    docs = vector_search(query, k=k)
    return "\n\n".join([doc['content'] + str(doc['metadata']) for doc in docs])