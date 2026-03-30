from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_community.document_loaders import UnstructuredPDFLoader
from src.core.db import get_vector_store



load_dotenv()

PG_CONNECTION = os.getenv("PG_CONNECTION_STRING")

def ingest_pdf(file_path):
    """Ingest a PDF file and save it in vector database"""
    #load the pdf from data folder and making them as langchain documents
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print("Pages: "+str(len(docs)))

    #enrich the document with metadata
    for doc in docs:
        doc.metadata.update({
            "source": file_path,
            "document_extension": "pdf",
            "page": doc.metadata.get("page", None),
            "category": "hr_support_desk",
            "last_updated": os.path.getmtime(file_path)

        })
    
    # split the text into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,         # character-based chunking
        chunk_overlap=200       # overlap of 100 characters between chunks to maintain context
    )

    chunks = splitter.split_documents(docs)
    print("Chunks: "+str(len(chunks)))


    vector_store = get_vector_store(collection_name="hr_support_desk")

    vector_store.add_documents(chunks)
    print("Ingestion completed successfully")

    # $env:PYTHONPATH="."; uv run src/ingestion/ingestion.py (execution cmd)



if __name__=="__main__":
    ingest_pdf("file/HR_Support_Desk_KnowledgeBase.pdf")