from fastapi import APIRouter
from src.api.v1.schemas.query_schema import QueryRequest, QueryResponse
from src.api.v1.agents.agent import get_query_docs

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    
    results = get_query_docs(request.query, 5)

    return QueryResponse(
        query= request.query,
        results= results
    )
    