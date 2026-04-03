import os
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv(override=True)

PG_CONNECTION = os.getenv("PG_CONNECTION_STRING")

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model = os.getenv("GOOGLE_EMBEDDINGS_MODEL"),
        api_key = os.getenv("GOOGLE_API_KEY"),
        output_dimensionality=1536
    )

vector_store = None

def get_vector_store(collection_name: str = "regulatory_compliance"):
    global vector_store

    if vector_store is None:
        print("Initializing PGVector (only once)...")

        vector_store = PGVector(
            collection_name=collection_name,
            connection=PG_CONNECTION,
            embeddings=get_embeddings(),
            use_jsonb=True
        )
        
    return vector_store