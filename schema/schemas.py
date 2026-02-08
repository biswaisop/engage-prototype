from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Action (BaseModel):
    type: str
    payload: Dict[str, Any]

class GraphOutput (BaseModel):
    intent: str
    response: Optional[str]
    confidence: float
    actions: List[Action]

    