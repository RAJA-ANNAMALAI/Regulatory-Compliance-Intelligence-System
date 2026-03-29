from src.core.db import get_vector_store
from schemas.query_schema import QueryResult
from langchain.agents import create_agent
from langchain_core.tools import tool
from dotenv import load_dotenv

def get_similar_docs(query: str, k: int = 5):

    load_dotenv()

    @tool
    def retrieve_context(query: str) -> str:
        """
        Retrieves relevant context from vector store for a given query.
        """
        vector_store = get_vector_store()
        docs = vector_store.similarity_search(query, k=k)
        
        if not docs:
            return "No relevant documents found"
        
        return "\n\n".join([doc.page_content for doc in docs])
    

    my_agent = create_agent(
        model="google_genai:gemini-3.1-pro-preview",
        tools=[retrieve_context],
        system_prompt="""
        You are a helpful assistant,

        You MUST follow these rules:
        1. ALWAYS call the tool 'retrive_context' before answering
        2. NEVER answer without using the tool
        3. You SHOULD USE ONLY the retrieved context
        4. If answer is not found, say: "Answer not found in documents"
        
        Be precise and concise.
        """
    )

    agent_response = my_agent.invoke({
        "messages": [
            {"role":"user", "content": query}
        ]
    })

    answer = agent_response["messages"][-1].content

    return QueryResult(
        content=answer,
        metadata={"source": "agent"}
    )