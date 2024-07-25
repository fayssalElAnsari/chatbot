from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from src.util import chat_streamer
from src.dependencies import get_query_engine

router = APIRouter()


@router.get("/chat/v1/stream")
async def chat_stream(query: str, query_engine=Depends(get_query_engine)):
    if query_engine:
        response = query_engine.query(query)
        return StreamingResponse(chat_streamer(response), media_type="text/event-stream")
    raise HTTPException(
        status_code=503, detail="Query engine is not available. Please check the index loading process."
    )
