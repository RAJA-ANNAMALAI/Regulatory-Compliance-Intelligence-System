from src.core.db import get_vector_store

def get_similar_docs(query: str, k: int = 5):
    vector_store = get_vector_store()
    docs = vector_store.similarity_search(query, k=k)
    
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in docs
    ]