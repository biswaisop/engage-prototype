from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4

class DocStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"

class DocUploadRequest(BaseModel):
    """form data for upload endpoint"""
    org_id: str

class DocRecord(BaseModel):
    """Document stored in MongoDB docs collection"""
    doc_id: str = Field(default_factory=lambda: str(uuid4()))
    org_id: str
    filename: str
    filename: str
    file_type: DocType
    s3_key: str
    status: DocStatus = DocStatus.PENDING
    chunk_count: Optional[int] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class DocResponse(BaseModel):
    """Response after upload"""
    doc_id: str
    filename: str
    s3_key: str
    status: DocStatus
    message: str

class DocStatusResponse(BaseModel):
    """Response for status polling"""
    doc_id: str
    filename: str
    status: DocStatus
    chunk_count: Optional[int] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None