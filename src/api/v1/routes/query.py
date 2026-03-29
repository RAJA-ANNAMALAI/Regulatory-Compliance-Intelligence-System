from fastapi import APIRouter
from schemas.query_schema import QueryRequest, QueryResponse
from services.query_service import get_similar_docs

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    
    results = get_similar_docs(request.query)

    return QueryResponse(
        query= request.query,
        results= results
    )
    