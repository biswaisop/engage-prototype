import redis
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

class RedisMemoryService:
    def __init__(self, max_messages: int = 30, ttl_seconds: int = 259200):
        self.client = redis.Redis(
            host = os.getenv("REDIS_HOST", "localhost"),
            port = int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        self.max_messages = max_messages
        self.ttl = ttl_seconds

    def _key(self, thread_id: str) -> str:
        return f"chat:memory:{thread_id}"
    
    def _state_key(self, thread_id) -> str:
        return f"chat:state:{thread_id}"        

    def add_message(self, thread_id: str, role: str, content: str, metadata: Dict = None):
        """Add message to sliding window in redis"""
        key = self._key(thread_id=thread_id)
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
        pipe.execute()

    def get_message(self, thread_id: str, limit: int = None) -> list[Dict]:
        key = self._key(thread_id)
        limit = limit or self.max_messages
        messages = self.client.lrange(key, -limit, -1)
        return [json.loads(m) for m in messages]

    def get_context_string(self, thread_id: str, limit: int = 10) -> str:
        """Get formatted for llm"""
        messages = self.get_message(thread_id=thread_id, limit = limit)
        if not messages:
            return ""
        context_parts = []
        for msg in messages:
            role = msg["role"].upper()
            context_parts.append(f"{role}:{msg['content']}")

        return "\n".join(context_parts)

    def set_state(self, thread_id: str, state: Dict[str, Any]):
        """Store session state ( intent, slots, etc)"""
        key = self._state_key(thread_id=thread_id)
        self.client.setex(key, self.ttl, json.dumps(state))    

    def get_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Store session state intent"""
        key = self._state_key(thread_id)
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def clear(self, thread_id: str):
        """Clear thread memory"""
        self.client.delete(self._key(thread_id), self._state_key(thread_id))

    def refresh_ttl(self, thread_id: str):
        """Extend TTL on activity"""
        self.client.expire(self._key(thread_id), self.ttl)
        self.client.expire(self._state_key(thread_id), self.ttl)
