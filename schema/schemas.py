from pydantic import BaseModel
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
    messages: List[Dict[str, str]]        # Conversation history (auto-managed by checkpointer)
    org_id: str                           # Organization ID for multi-tenant
    intent: Optional[str]                 # Detected intent
    confidence: Optional[float]           # Intent confidence
    next_node: Optional[str]              # Next node to route to
    result: Optional[Dict[str, Any]]      # Node output