from fastapi import APIRouter
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.api.v1.services.query_service import handle_file_upload
from src.api.v1.agents.agent import get_query_docs
from src.api.v1.schemas.query_schema import QueryRequest, QueryResponse, QueryResult, UploadResponse

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    
    results = get_query_docs(request.query, 5)

    return QueryResponse(
        query= request.query,
        results= results
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        filename = handle_file_upload(file)

        return UploadResponse(
            message="File uploaded and ingested successfully",
            filename=filename
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))