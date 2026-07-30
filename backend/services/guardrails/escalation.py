from typing import Optional
from datetime import datetime, timezone

from services.redis_memory import RedisClient
from schema.guardrails import EscalationState, GuardLayer, GuardResult, GuardAction


class EscalationService:
    """
    Per-request service — instantiated via FastAPI dependency injection,
    same pattern as RedisMemoryService.
    """

    def __init__(self, threshold: int = 3, ttl_seconds: int = 3600):
        self.client = RedisClient.get()
        self.threshold = threshold
        self.ttl = ttl_seconds

    # ── Key helper ────────────────────────────────────────────────
    def _key(self, thread_id: str, org_id: str) -> str:
        return f"guard:escalation:{org_id}:{thread_id}"

    # ── Core operations ──────────────────────────────────────────
    async def get_state(self, thread_id: str, org_id: str) -> EscalationState:
        key = self._key(thread_id=thread_id, org_id=org_id)
        data = await self.client.hgetall(key)

        if not data:
            return EscalationState(
                org_id=org_id, conversation_id=thread_id, threshold=self.threshold
            )

        return EscalationState(
            org_id=org_id,
            conversation_id=thread_id,
            count=int(data.get("count", 0)),
            last_triggered_layer=data.get("last_triggered_layer") or None,
            last_triggered_at=datetime.fromisoformat(data["last_triggered_at"])
            if data.get("last_triggered_at")
            else None,
            threshold=self.threshold,
        )

    async def record_trigger(
        self, thread_id: str, org_id: str, layer: GuardLayer
    ) -> EscalationState:
        """Call whenever any guardrail layer blocks or flags a message."""
        key = self._key(thread_id=thread_id, org_id=org_id)
        now = datetime.now(timezone.utc).isoformat()

        pipe = self.client.pipeline()
        pipe.hincrby(key, "count", 1)
        pipe.hset(key, mapping={
            "last_triggered_layer": layer.value,
            "last_triggered_at": now,
        })
        pipe.expire(key, self.ttl)
        results = await pipe.execute()

        new_count = results[0]  # hincrby's return value

        return EscalationState(
            org_id=org_id,
            conversation_id=thread_id,
            count=new_count,
            last_triggered_layer=layer,
            last_triggered_at=datetime.fromisoformat(now),
            threshold=self.threshold,
        )

    async def reset(self, thread_id: str, org_id: str) -> None:
        """Call after a successful human handoff, or manual staff resolution."""
        await self.client.delete(self._key(thread_id=thread_id, org_id=org_id))

    # ── Entrypoint for nodes ─────────────────────────────────────
    async def check_and_record(
        self, thread_id: str, org_id: str, layer: GuardLayer
    ) -> GuardResult:
        state = await self.record_trigger(thread_id=thread_id, org_id=org_id, layer=layer)

        if state.should_handoff:
            return GuardResult(
                safe=False,
                action=GuardAction.ESCALATE,
                layer=GuardLayer.ESCALATION,
                reason=f"escalation_threshold_reached:{state.count}/{self.threshold}",
            )

        return GuardResult(
            safe=True,
            action=GuardAction.ALLOW,
            layer=GuardLayer.ESCALATION,
            reason=f"escalation_count:{state.count}/{self.threshold}",
        )