from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum

Base = declarative_base()

class ConversationState(str, enum.Enum):
    AI_ACTIVE = "AI_ACTIVE"
    HUMAN_REQUESTED = "HUMAN_REQUESTED"
    HUMAN_CONNECTED = "HUMAN_CONNECTED"
    CLOSED = "CLOSED"

class SenderType(str, enum.Enum):
    VISITOR = "VISITOR"
    AI = "AI"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"

def utc_now():
    return datetime.now(timezone.utc)

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    config = Column(JSON, default={})
    plan = Column(String(50), default="FREE")
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    conversations = relationship("Conversation", back_populates="organization")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    visitor_id = Column(UUID(as_uuid=True), nullable=False)
    visitor_name = Column(String(255))
    visitor_metadata = Column(JSON, default={})
    state = Column(String(50), default=ConversationState.AI_ACTIVE.value)
    agent_id = Column(UUID(as_uuid=True), nullable=True)
    handoff_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    connected_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String(50), nullable=False)
    sender_id = Column(UUID(as_uuid=True), nullable=True)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, default={})
    client_message_id = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    conversation = relationship("Conversation", back_populates="messages")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    contact_info = Column(JSON, nullable=False)
    intent_type = Column(String(50), nullable=False)
    intent_details = Column(JSON, default={})
    source = Column(String(50), nullable=False)
    status = Column(String(50), default="new")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class Issue(Base):
    __tablename__ = "issues"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)
    issue_metadata = Column(JSON, default={})
    source = Column(String(50), nullable=False)
    status = Column(String(50), default="OPEN")
    external_ticket_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

