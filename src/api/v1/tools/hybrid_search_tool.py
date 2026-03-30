from langchain_core.tools import tool
from src.api.v1.services.query_service import _hybrid_search

@tool
def hybrid_tool(query: str,k: int):
    """
    Use this tool for complex queries that need both keywords and context.
    if the query is short (3 words or fewer), 
    treat it as a hybrid case to balance precision and recall
    """
    docs = _hybrid_search(query,k=k)
    return "\n\n".join([doc['content'] + str(doc['metadata']) for doc in docs])