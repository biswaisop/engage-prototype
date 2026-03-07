from pydantic import BaseModel, Field
from typing import List, Any, Dict, Optional
from enum import Enum
from datetime import datetime, timezone

class chatMessageRequest(BaseModel):
    thread_id: str
    message: str
    org_id: str

class chatMessageResponse(BaseModel):
    response: str
    thread_id: str
    org_id: str

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
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    thread_id: str
    org_id: str
    message: str
    user_id: Optional[str] = None