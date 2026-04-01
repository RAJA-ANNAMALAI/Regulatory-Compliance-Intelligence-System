from dotenv import load_dotenv # uv add python-dotenv
import os
import re
from langchain_community.document_loaders import PyPDFLoader # uv add langchain-community pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings #uv add langchain-googgle-genai
from langchain_postgres import PGVector # uv add langchain-postgres
from src.core.db import get_vector_store
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader
)

load_dotenv(override=True)

PG_CONNECTION = os.getenv("PG_CONNECTION_STRING")

def load_document(file_path: str, ext: str):
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)

    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")

    elif ext == ".docx":
        loader = UnstructuredWordDocumentLoader(file_path)

    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return loader.load()



def ingest_document(file_path: str, ext: str):
    # Step 1: Load document
    documents = load_document(file_path, ext)
    print(f"Loaded {len(documents)} pages")

    # Step 2: Add metadata
    for doc in documents:
        doc.metadata.update({
             "source": file_path,
            "document_extension": "pdf",
            "page": doc.metadata.get("page", None),
            "category": "hr_support_desk",
            "last_updated": os.path.getmtime(file_path)
        })

    # Step 3: Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)
    print(f"Total chunks created: {len(chunks)}")

    # Step 4: Store in PGVector
    vector_store = get_vector_store()

    vector_store.add_documents(chunks)

    print("✅ Ingestion completed and stored in DB")


    # $env:PYTHONPATH="."
    # uv run src/ingestion/ingestion.py