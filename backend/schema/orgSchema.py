from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Organization(BaseModel):
    org_id: str
    name: str
    plan: PlanType = PlanType.FREE

    #contact and identity
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[str] = None

    #chatbot_config
    bot_name: str = "Front Desk Assistant"
    allowed_intents: List[str] = [
        "INFORMATION_RETRIEVAL",
        "LEAD_CAPTURE",
        "ISSUE_COMPLAINT",
        "HANDOFF_REQUEST",
        "CHAT"
    ]

    #Knowledge Base
    vector_space: str
    
    #memory_settings (overrides defaults)
    max_memory_size: int = 20
    memory_ttl_seconds: int = 259200

    #status
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


print(datetime.now(timezone.utc))