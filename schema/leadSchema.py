from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone

# class leadForm(BaseModel):
#     thread_id: str
#     org_id: str
#     email: EmailStr
#     phone: Optional[str]
#     check_in: str
#     check_out: str
#     room_type: Optional[str]
#     guest_count: Optional[str]
#     notes: Optional[str]

# class leadResponse(BaseModel):
#     thread_id: str
#     message: str
#     timestamp: str

class leadForm(BaseModel):
    thread_id: str
    org_id: str
    email: EmailStr
    phone: Optional[str] = None
    check_in: str
    check_out: str
    room_type: Optional[str] = None
    guest_count: Optional[str] = None
    notes: Optional[str] = None

class leadResponse(BaseModel):
    thread_id: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class leadExtraction(BaseModel):
    """pre-extracted fields from conversation for form data"""
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    room_type: Optional[str] = None
    guest_count: Optional[str] = None
    notes: Optional[str] = None


class leadDocument(BaseModel):
    """Document stored in mongoDB org_id.leads collectin"""
    thread_id: str
    org_id: str
    email: str
    phone: Optional[str] = None
    check_in: str
    check_out: str
    room_type: Optional[str] = None
    guest_count: Optional[str] = None
    notes: Optional[str] = None
    source: str = "CHAT"
    status: str = "NEW"
    created_at: datetime = datetime.now(timezone.utc)