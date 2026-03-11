import redis.asyncio as aioredis
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class RedisClient:
    """Singleton async Redis connection"""
    _client: aioredis.Redis = None

    @classmethod
    def connect(cls):
        if cls._client is None:
            cls._client = aioredis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True
            )
            logger.info("Redis connected")

    @classmethod
    def disconnect(cls):
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            logger.info("Redis disconnected")

    @classmethod
    def get(cls) -> aioredis.Redis:
        if cls._client is None:
            raise RuntimeError("Redis not connected, call RedisClient.Connect first")
        return cls._client

    @classmethod
    async def ping(cls) -> bool:
        try:
            await cls.get().ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False


class RedisMemoryService:
    """
    Per-request service — instantiated with org-specific settings
    via FastAPI dependency injection.
    """

    def __init__(self, max_messages: int = 30, ttl_seconds: int = 259200):
        self.client = RedisClient.get()
        self.max_messages = max_messages
        self.ttl = ttl_seconds

    # ── Key helpers ───────────────────────────────────────────────
    def _key(self, thread_id: str, org_id: str) -> str:
        return f"chat:memory:{org_id}:{thread_id}"

    def _state_key(self, thread_id: str, org_id: str) -> str:
        return f"chat:state:{org_id}:{thread_id}"

    # ── Messages ──────────────────────────────────────────────────
    async def add_message(self, thread_id: str, org_id: str, role: str, content: str, metadata: Dict = None):
        """Add message to sliding window in redis"""
        key = self._key(thread_id=thread_id, org_id=org_id)
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }

        pipe = self.client.pipeline()
        pipe.rpush(key, json.dumps(message))
        pipe.ltrim(key, -self.max_messages, -1)
        pipe.expire(key, self.ttl)
        await pipe.execute()

    async def get_message(self, thread_id: str, org_id: str, limit: int = None) -> List[Dict]:
        key = self._key(thread_id=thread_id, org_id=org_id)
        limit = limit or self.max_messages
        messages = await self.client.lrange(key, -limit, -1)
        return [json.loads(m) for m in messages]

    async def get_context_string(self, thread_id: str, org_id: str, limit: int = 10) -> str:
        """Get formatted for llm"""
        messages = await self.get_message(thread_id=thread_id, org_id=org_id, limit=limit)
        if not messages:
            return ""
        return "\n".join(
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in messages
        )

    async def set_state(self, thread_id: str, org_id: str, state: Dict[str, Any]):
        """Store session state ( intent, slots, etc)"""
        key = self._state_key(thread_id=thread_id, org_id=org_id)
        await self.client.setex(key, self.ttl, json.dumps(state))

    async def get_state(self, thread_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        """Store session state intent"""
        key = self._state_key(thread_id=thread_id, org_id=org_id)
        data = await self.client.get(key)
        return json.loads(data) if data else None

    # ── Lifecycle ─────────────────────────────────────────────────
    async def clear(self, thread_id: str, org_id: str):
        """Clear thread memory"""
        await self.client.delete(self._key(thread_id=thread_id, org_id=org_id), self._state_key(thread_id=thread_id, org_id=org_id))

    async def refresh_ttl(self, thread_id: str,  org_id: str):
        """Extend TTL on activity"""
        await self.client.expire(self._key(thread_id = thread_id, org_id=org_id), self.ttl)
        await self.client.expire(self._state_key(thread_id=thread_id, org_id=org_id), self.ttl)
