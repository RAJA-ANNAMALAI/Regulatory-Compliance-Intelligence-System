from fastapi import APIRouter
from src.api.v1.schemas.query_schema import QueryRequest, QueryResponse
from src.api.v1.services.query_service import get_similar_docs

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    
    results = get_similar_docs(request.query)

    return {
        "query": request.query,
        "results": results
    }