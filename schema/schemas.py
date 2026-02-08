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

class GraphState(TypedDict):
    message: str
    history: List[Dict[str, Any]] = []
    intent: Optional[str] = None
    confidence: Optional[float] = None
    next_node: Optional[str] = None
    result: Optional[Dict[str, Any]] = None