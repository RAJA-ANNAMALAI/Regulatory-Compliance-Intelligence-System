from langchain_core.tools import tool
from src.api.v1.services.query_service import fts_search

@tool
def keyword_search_tool(query: str,k:  int):
    """
    Use this tool for exact keyword matching.
    Best for policy IDs, technical terms, or specific acronyms.
    """
    docs = fts_search(query,k=k)
    return "\n\n".join([doc['content'] + str(doc['metadata']) for doc in docs])