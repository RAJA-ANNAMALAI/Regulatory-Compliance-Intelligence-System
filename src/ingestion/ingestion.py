
from dotenv import load_dotenv # uv add python-dotenv
import os
import re
from langchain_community.document_loaders import PyPDFLoader # uv add langchain-community pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings #uv add langchain-googgle-genai
from langchain_postgres import PGVector # uv add langchain-postgres
from src.core.db import get_vector_store

load_dotenv()

PG_CONNECTION = os.getenv("PG_CONNECTION_STRING")

def ingest_pdf(file_path):
    """Ingest a PDF file and save it in vector database"""
    # 1. load the pdf from the data folder
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print("Pages: "+str(len(docs)))

    # 2. enrich the document with metadata
    for doc in docs:
        # add the file path, page number, and other relevant metadata to the document
        doc.metadata.update({
            "source":file_path,
            "document_extension":"pdf",
            "page":doc.metadata.get("page", None),
            "category":"hr_support_desk",
            "last_updated":os.path.getmtime(file_path)
        })

    # 3. split the text into chunks
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size = 512, # tokens
        chunk_overlap = 100, # tokens
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = splitter.split_documents(docs)
    print("Chunks: "+str(len(chunks)))

    # 4 + 5. Embeddings + store (delegated to core/db)
    vector_store = get_vector_store(collection_name="hr_support_desk")

    vector_store.add_documents(chunks)

    print("Ingestion completed successfully")

    # open ai model
    '''embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )'''

if __name__ == "__masin__":
    ingest_pdf("data/HR_Support_Desk.pdf")

# to execute : $env:PYTHONPATH="."
# uv run src/ingestion/ingestion.py