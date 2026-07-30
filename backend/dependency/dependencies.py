# dependency/dependencies.py
from fastapi import Depends, Query, HTTPException
from services.redis_memory import RedisMemoryService
from db.connection import MongoDb


async def _load_redis_memory(org_id: str) -> RedisMemoryService:
    """Plain, framework-agnostic loader. No Query(), no HTTPException.
    Safe to call directly from HTTP deps or websocket loops."""
    org = await MongoDb.orgs().find_one({"org_id": org_id})
    if not org:
        raise ValueError(f"Org '{org_id}' not found")
    return RedisMemoryService(
        max_messages=org.get("max_messages", 30),
        ttl_seconds=org.get("ttl_seconds", 259200),
    )


async def get_redis_memory(org_id: str = Query(...)) -> RedisMemoryService:
    """HTTP-only. Used via Depends() - resolves org_id from the query string."""
    try:
        return await _load_redis_memory(org_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load org config: {str(e)}")


async def get_redis_memory_for_ws(org_id: str) -> RedisMemoryService:
    """Websocket-only. Call directly with a plain org_id string, no Query().
    Raises plain ValueError - caller must catch and send a JSON error frame,
    never let HTTPException reach a websocket connection."""
    return await _load_redis_memory(org_id)


# dependency/dependencies.py — add alongside your existing redis memory deps

from services.guardrails.escalation import EscalationService


async def _load_escalation_service(org_id: str) -> EscalationService:
    """Plain, framework-agnostic loader — mirrors _load_redis_memory."""
    org = await MongoDb.orgs().find_one({"org_id": org_id})
    if not org:
        raise ValueError(f"Org '{org_id}' not found")
    return EscalationService(
        threshold=org.get("guardrail_escalation_threshold", 3),
        ttl_seconds=org.get("guardrail_escalation_ttl", 3600),
    )


async def get_escalation_service(org_id: str = Query(...)) -> EscalationService:
    """HTTP-only."""
    try:
        return await _load_escalation_service(org_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load org config: {str(e)}")


async def get_escalation_service_for_ws(org_id: str) -> EscalationService:
    """Websocket-only — plain org_id, raises ValueError, caller catches it."""
    return await _load_escalation_service(org_id)