from fastapi import APIRouter, Query, HTTPException
from utils.redis_memory import RedisMemoryService
from schema.chatSchema import chatHistoryResponse
router = APIRouter()
redis_memory = RedisMemoryService()



@router.get("/", response_model=chatHistoryResponse)
async def get_chat_history(thread_id: str = Query(...)):
    try:
        messages = redis_memory.get_message(thread_id=thread_id)
        return chatHistoryResponse(
            thread_id=thread_id,
            messages=messages
        )
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"failed to retrieve history: {str(e)}")