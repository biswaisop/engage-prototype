from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any, TypedDict

class Action (BaseModel):
    type: str
    payload: Dict[str, Any]

class GraphOutput (BaseModel):
    intent: str
    response: Optional[str]
    confidence: float
    actions: List[Action]

class IntentResult(BaseModel):
    intent: str
    confidence: float 

class GraphState(TypedDict, total=False):
    """State shared across all graph nodes."""
    message: str                          # Current user input  
    thread_id: str      # Conversation history (auto-managed by checkpointer)
    org_id: str                           # Organization ID for multi-tenant
    intent: Optional[str]                 # Detected intent
    confidence: Optional[float]           # Intent confidence
    next_node: Optional[str]              # Next node to route to
    context: Optional[str]
    result: Optional[Dict[str, Any]]      # Node output


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

class leadForm(BaseModel):
    thread_id: str
    org_id: str
    email: EmailStr
    phone: Optional[str]
    check_in: str
    check_out: str
    room_type: Optional[str]
    guest_count: Optional[str]
    notes: Optional[str]

class leadResponse(BaseModel):
    thread_id: str
    message: str
    timestamp: str