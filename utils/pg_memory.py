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
            db.add(conversation)
            db.flush()
        return conversation

    def get_history(
            self,
            db:Session,
            conversation_id: uuid.UUID,
            max_turns: int = 6,
    ) -> List[Dict[str, str]]:
        """ Get conversation history from PostgreSQL.
        Returns last `max_turns` exchanges."""

        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
        ).order_by(
            desc(Message.created_at)
        ).limit(max_turns*2).all()

        messages = list(reversed(messages))

        history = []

        for msg in messages:
            role = "assistant" if msg.sender_type in ["AI", "AGENT"] else "user"
            history.append({
                "role": role,
                "content": msg.content
            })
        return history
    
    def add_messages(
            self,
            db: Session,
            conversation_id: uuid.UUID,
            content: str,
            sender_type: str,
            sender_id: uuid.UUID = None,
            message_metadata: Dict = None
    ) -> Message:
        """Add a message to the conversation"""
        message = Message(
            conversation_id = conversation_id,
            sender_type = sender_type,
            sender_id = sender_id,
            content = content,
            message_metadata = message_metadata or {}
        )
        db.add(message)
        db.flush()
        return message
    
    def add_exchange(
            self,
            db: Session,
            conversation_id: uuid.UUID,
            user_message: str,
            assistant_response: str,
            assistant_type: str = "AI"
    ) -> tuple:
        """Add a user message and response."""
        user_msg = self.add_messages(db, conversation_id, user_message, "VISITOR")
        assistant_msg = self.add_messages(db, conversation_id, assistant_response, assistant_type)
        return user_msg, assistant_msg
    
    @staticmethod
    def format_for_llm(history: List[Dict[str, str]]) -> list[Dict[str, str]]:
        """Format history for llm use"""
        return history
    
    @staticmethod
    def build_messages(
        query: str,
        system_prompt: str,
        history: List[Dict[str, str]] = None,
        context: str = None,
    ) -> List[Dict[str, str]]:
        """Build complete messages for LLM invocation."""
        messages = []

        # Add system prompt
        messages.append({"role": "system", "content": system_prompt})

        # Add context if provided
        if context:
            messages.append({
                "role": "system",
                "content": f"Knowledge Base Context:\n{context}"
            })

        # Add conversation history
        if history:
            messages.extend(history)

        # Add current user query
        messages.append({"role": "user", "content": query})

        return messages


pg_memory = PostgresMemory()