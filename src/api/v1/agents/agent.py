from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.api.v1.tools.fts_search_tool import keyword_search_tool
from src.api.v1.tools.vector_search_tool import semantic_search_tool
from src.api.v1.tools.hybrid_search_tool import hybrid_tool
from src.api.v1.schemas.query_schema import QueryResult
import time
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv(override = True)

class AIResponse(BaseModel):
    """Structured Response from AI"""

    ans: str = Field(description="Answer for the given query")
    page: int = Field(description= "page number")
    source: str = Field(description= "pdf file_name")


def get_query_docs(query: str, k: int ):

    model = ChatGoogleGenerativeAI(
        model = "gemini-2.5-flash",
        temperature = 0
    )
    
    my_agent = create_agent(
        model= model,
        tools=[keyword_search_tool,semantic_search_tool,hybrid_tool],
        response_format=AIResponse,
        system_prompt="""
        You are a helpful assistant,

        You MUST follow these rules:

        1. ALWAYS call one of the search tools before answering policy questions.
        You should select the search tool based on the given criteria below:
            1)If the query is long and doesn't match any specific keyword patterns, use semantic_search_tool.
            2)if the keyword patterns match anywhere in the query, use keyword_search_tool.
            Keyword patterns examples:  policy/ticket codes: POL-2024-HR-007, short uppercase abbreviations: LTA, CTC, ESI,
        long numeric IDs / employee numbers.
            3)if the query is short (3 words or fewer), treat it as a hybrid case to balance precision and recall and use hybrid_tool.
        2. NEVER answer without using a tool.
        3. You SHOULD USE ONLY the retrieved context from that tool's output.Understand the query and retrived chunks fully and
        give personalized answer, not just pasting the same thing in the document.
        4. If answer is not found, say: "Answer not found in documents".And give page number and source as NA.
        5. From any tool, you will receive a set of chunks with contains answer for the query along with its metadata.
        You should select the most appropriate chunk as answer and its corressponding metadata.
       
        
        Be precise and concise.
        """
    )

    # This change should fix the error: pass the messages as a dictionary, not a list
    agent_response = my_agent.invoke({
        "messages":[
            {"role":"user","content":query}
        ]
    })

    answer : AIResponse = agent_response["structured_response"]

    if answer.source == "N/A":
        answer.page = "N/A"
    else:
        answer.page += 1
 
    return [QueryResult(
        content= answer.ans,
        metadata={
            "page": answer.page,
            "source": answer.source
        }
    )]