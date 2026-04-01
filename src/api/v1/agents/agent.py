from langchain.agents import create_agent
from src.api.v1.tools.fts_search_tool import keyword_search_tool
from src.api.v1.tools.vector_search_tool import semantic_search_tool
from src.api.v1.tools.hybrid_search_tool import hybrid_tool
from src.api.v1.schemas.query_schema import QueryResult
import re
import time
from dotenv import load_dotenv

load_dotenv(override = True)


def get_query_docs(query: str, k: int ):
    my_agent = create_agent(
        model="google_genai:gemini-2.5-flash",
        tools=[keyword_search_tool,semantic_search_tool,hybrid_tool],
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
        3. You SHOULD USE ONLY the retrieved context from that tool's output.
        4. If answer is not found, say: "Answer not found in documents"
        5. From any tool, you will receive a set of chunks with contains answer for the query along with its metadata.
        You should select the most appropriate chunk as answer and its corressponding metadata.
        6. Finally, you MUST return your answer as a single string using the following exact template. 
        Use uppercase labels followed by a colon.

        ANSWER: [Insert concise answer here]
        PAGE: [Insert page number]
        SOURCE: [Insert filename]
        CONFIDENCE SCORE: [Insert cofidence score from metadata]

        Do not include any other text or JSON braces.
        
        Be precise and concise.
        """
    )


    # This change should fix the error: pass the messages as a dictionary, not a list
    agent_response = my_agent.invoke({
        "messages":[
            {"role":"user","content":query}
        ]
    })

    last_msg = agent_response["messages"][-1]

    if isinstance(last_msg.content, list):
        raw_text = last_msg.content[0].get("text","")
    else:
        raw_text = last_msg.content

    answer_match = re.search(r"ANSWER:\s*(.*?)(?=\s*PAGE:|$)", raw_text, re.DOTALL)
    page_match   = re.search(r"PAGE:\s*(.*?)(\s*SOURCE:|$)", raw_text)
    source_match = re.search(r"SOURCE:\s*(.*)", raw_text)
    conf_match = re.search(r"CONFIDENCE:\s*(.*)",raw_text)

    clean_answer = answer_match.group(1).strip() if answer_match else raw_text
    page_val     = page_match.group(1).strip() if page_match else "N/A"
    source_val   = source_match.group(1).strip() if source_match else "Unknown"
    raw_conf = conf_match.group(1).strip() if conf_match else "0.0"
    clean_conf =float(raw_conf) / 100.0


     
    return [QueryResult(
        content=clean_answer,
        metadata={
            "page": int(page_val) + 1,
            "source": source_val,
            "confidence": clean_conf
        }
    )]