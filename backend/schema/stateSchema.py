from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from services.redis_memory import RedisMemoryService   

class Action (BaseModel):
    type: str
    payload: Dict[str, Any]

class GraphOutput (BaseModel):
    intent: str
    response: Optional[str]
    actions: List[Action]

class IntentResult(BaseModel):
    intent: str


class GraphState(TypedDict, total=False):
    """State shared across all graph nodes."""
    # message: str                          # Current user input  
    # thread_id: str      # Conversation history (auto-managed by checkpointer)
    # org_id: str                           # Organization ID for multi-tenant
    # intent: Optional[str]                 # Detected intent          
    # next_node: Optional[str]              # Next node to route to
    # context: Optional[str]
    # result: Optional[Dict[str, Any]]      # Node output
    # redis_memory: Optional[Any] 
    message: str
    messages: List[Dict[str, str]]
    thread_id: str
    org_id: str
    intent: Optional[str]
    confidence: Optional[float]
    context: Optional[str]
    result: Optional[Dict]
    redis_memory: Optional[Any]   # ← add this



