"""
PostgreSQL-backed memory for LangGraph.
Replaces in-memory checkpointer with persistent storage.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid

from db import get_db, Conversation, Message, SenderType

class PostgresMemory:
    """
    PostgreSQL-backed conversation memory.
    Stores all messages persistently and retrieves history for LLM context.
    """

    def get_or_create_conversation(
            self, db: Session,
            thread_id: str,
            org_id: str, 
            visitor_id: str = None
    ) -> Conversation:
        """Get existing conversation or create a new one"""
        try:
            conv_uuid = uuid.UUID(thread_id)
        except ValueError:
            conv_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, thread_id)

        conversation = db.query(Conversation).filter(
            Conversation.id == conv_uuid,
            Conversation.org_id == uuid.UUID(org_id) if isinstance(org_id, str) else org_id
        ).first()

        if not conversation:
            conversation = Conversation(
                id = conv_uuid,
                org_id = uuid.UUID(org_id) if isinstance(org_id, str) else org_id,
                visitor_id = uuid.UUID(visitor_id)if visitor_id else uuid.uuid4(),
                state = "AI_ACTIVE"
            )