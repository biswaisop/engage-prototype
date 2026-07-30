from enum import Enum
from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class GuardAction(BaseModel):
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"


class GuardLayer(BaseModel):
    INPUT_GUARD = "input_guard"
    SYSTEM_PROMPT = "system_prompt"
    CRITIC = "critic"
    OUTPUT_FILTER = "output_filter"
    ESCALATION = "escalation"


class GuardResult(BaseModel):
    """Standard return shape for every guardrail layer."""
    safe: bool
    action: GuardAction
    layer: GuardLayer
    reason: Optional[str] = None
    # populated when action == BLOCK, this is what gets sent to the user instead
    fallback_response: Optional[str] = None


class CriticVerdict(BaseModel):
    """Structured output expected from the critic agent's llm call."""
    safe: bool
    reason: Optional[str] = None
    flagged_category: Optional[
        Literal[
            "prompt_leak",
            "unauthorized_commitment",
            "competitor_mention",
            "persona_break",
            "data_leak",
            "off_topic",
        ]
    ] = None

class EscalationState(BaseModel):
    """Mirrors what you store in Redis per-conversation."""
    org_id: str
    conversation_id: str
    count: int = 0
    last_triggered_layer: Optional[GuardLayer] = None
    last_triggered_at: Optional[datetime] = None
    threshold: int = 3

    @property
    def should_handoff(self) -> bool:
        return self.count >= self.threshold

class FlaggedMessage(BaseModel):
    """Persisted to MongoDB for staff review / audit trail."""
    org_id: str
    conversation_id: str
    guest_message: str
    layer: GuardLayer
    reason: Optional[str] = None
    action_taken: GuardAction
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GuardrailConfig(BaseModel):
    """Per-tenant guardrail settings, pulled from your hotel config in MongoDB."""
    org_id: str
    escalation_threshold: int = 3
    input_guard_enabled: bool = True
    critic_enabled: bool = True
    banned_topics: list[str] = Field(default_factory=list)
    system_prompt_override: Optional[str] = None