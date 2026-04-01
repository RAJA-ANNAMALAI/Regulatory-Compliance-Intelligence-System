from langchain_core.tools import tool
from src.api.v1.services.query_service import vector_search

@tool
def semantic_search_tool(query: str,k: int):
    """
    Use this tool for natural language questions.
    Ideal for understanding context, feelings, or broad HR topics.
    """
    docs = vector_search(query, k=k)
    return "\n\n".join([
    f"Content: {doc['content']}\nSource: {doc['metadata'].get('source')}\nPage: {doc['metadata'].get('page')}" 
    for doc in docs
    ])