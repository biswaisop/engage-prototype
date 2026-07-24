from pydantic import BaseModel, Field
from typing import List, Any, Dict, Optional
from enum import Enum
from datetime import datetime, timezone

class ConversationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"
    HANDED_OFF = "HANDED_OFF"

class chatMessageResponse(BaseModel):
    response: str
    thread_id: str
    org_id: str
    actions: List[Dict[str, Any]] = []

class chatHistoryResponse(BaseModel):
    thread_id: str
    message: List[Any]

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Conversation(BaseModel):
    thread_id: str
    org_id: str
    user_id: Optional[str] = None
    lead_id: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: ConversationStatus = ConversationStatus.ACTIVE
    intent_history: List[str] = Field(default_factory=list)


class chatMessageRequest(BaseModel):
    thread_id: str
    org_id: str
    message: str
    user_id: Optional[str] = None 