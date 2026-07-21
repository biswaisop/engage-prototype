from fastapi import Depends, Query, HTTPException
from services.redis_memory import RedisMemoryService
from db.connection import MongoDb


async def get_redis_memory(org_id: str = Query(...)) -> RedisMemoryService:
    try:
        org = await MongoDb.orgs().find_one({"org_id": org_id})
        if not org:
            raise HTTPException(status_code=404, detail=f"Org '{org_id}' not found")
        return RedisMemoryService(
            max_messages=org.get("max_messages", 30),
            ttl_seconds=org.get("ttl_seconds", 259200),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load org config: {str(e)}")