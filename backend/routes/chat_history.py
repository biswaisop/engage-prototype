from fastapi import APIRouter, Query, HTTPException, Depends
from services.redis_memory import RedisMemoryService
from schema.chatSchema import chatHistoryResponse
from dependency.dependencies import get_redis_memory

router = APIRouter()




@router.get("/", response_model=chatHistoryResponse)
async def get_chat_history(
        thread_id: str = Query(...),
        org_id: str = Query(...),
        redis_memory: RedisMemoryService = Depends(get_redis_memory)
):
    try:
        messages = await redis_memory.get_message(thread_id = thread_id, org_id=org_id)
        return chatHistoryResponse(
            thread_id = thread_id,
            message = messages
        )
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"failed to retrieve history: {str(e)}")