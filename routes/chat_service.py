# routers/chat.py
from datetime import datetime, timezone
import asyncio

from fastapi import APIRouter, HTTPException, status, Depends

from schema.chatSchema import chatMessageResponse, chatMessageRequest
from schema.stateSchema import GraphState
from graph import graph
from services.redis_memory import RedisMemoryService
from dependency.dependencies import get_redis_memory
from db.connection import MongoDb  # adjust to your actual import path

semaphore = asyncio.Semaphore(20)

router = APIRouter()


@router.post("/", response_model=chatMessageResponse)
async def chat_message(
        request: chatMessageRequest,
        redis_memory: RedisMemoryService = Depends(get_redis_memory)
):
    try:

        # 1. Org must exist before anything else happens
        org = await MongoDb.orgs().find_one({"org_id": request.org_id})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # 2. Ensure a conversation record exists for this thread (create on first message)
        await MongoDb.conversations().update_one(
            {"org_id": request.org_id, "thread_id": request.thread_id},
            {
                "$setOnInsert": {
                    "org_id": request.org_id,
                    "thread_id": request.thread_id,
                    "created_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )

        async with semaphore:
            state = GraphState(
                thread_id=request.thread_id,
                message=request.message,
                org_id=request.org_id,
                redis_memory=redis_memory,
            )
            # NOTE: LangGraph checkpointer expects thread_id nested under "configurable"
            config = {"configurable": {"thread_id": request.thread_id}}

            new_state = await graph.ainvoke(state, config=config)
            response_text = new_state.get("result", {}).get("response", "")
            actions = new_state.get("result", {}).get("actions", [])
            thread_id = new_state.get("thread_id", request.thread_id)

            if response_text is None or not response_text:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Invalid graph response structure"
                )

            # 3. Persist both turns of this exchange to Mongo
            await MongoDb.conversations().update_one(
                {"org_id": request.org_id, "thread_id": thread_id},
                {
                    "$push": {
                        "messages": {
                            "$each": [
                                {
                                    "role": "user",
                                    "content": request.message,
                                    "timestamp": datetime.now(timezone.utc),
                                },
                                {
                                    "role": "assistant",
                                    "content": response_text,
                                    "timestamp": datetime.now(timezone.utc),
                                },
                            ]
                        }
                    },
                    "$set": {"updated_at": datetime.now(timezone.utc)},
                },
            )

            return chatMessageResponse(
                response=response_text,
                thread_id=thread_id,
                org_id=request.org_id,
                actions = actions
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")