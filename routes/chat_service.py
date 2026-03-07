from schema import chatMessageResponse, chatMessageRequest
from schema.stateSchema import GraphState
from graph import graph
from fastapi import APIRouter, HTTPException, status
import asyncio

semaphore = asyncio.Semaphore(20)

router = APIRouter()

@router.post("/", response_model=chatMessageResponse)
async def chat_message(request: chatMessageRequest):
    try:
        async with semaphore:
            state = GraphState(thread_id=request.thread_id, message=request.message, org_id=request.org_id)
            config = {"thread_id": request.thread_id}
            new_state = await graph.ainvoke(state, config=config)
            response_text = new_state.get("result", {}).get("response", "")
            thread_id = new_state.get("thread_id", request.thread_id)
            if response_text is None:
                raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid graph response structure"
            )
            return chatMessageResponse(
                response=response_text,
                thread_id=thread_id,
                org_id=request.org_id
            )
    except HTTPException as e:
        raise HTTPException(
        status_code=500,
        detail="Chat processing failed"
    )