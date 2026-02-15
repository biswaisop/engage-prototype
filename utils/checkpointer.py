"""
Custom PostgreSQL checkpointer for LangGraph.
Stores graph state in PostgreSQL for persistence across restarts.
"""
from typing import Any, Dict, Optional, Tuple
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
import json

from db import SessionLocal, engine, Base


def utc_now():
    return datetime.now(timezone.utc)


class CheckpointRecord(Base):
    """SQLAlchemy model for storing checkpoints."""
    __tablename__ = "langgraph_checkpoints"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(String(255), nullable=False, index=True)
    checkpoint_id = Column(String(255), nullable=False)
    parent_id = Column(String(255), nullable=True)
    checkpoint_data = Column(Text, nullable=True)
    metadata_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class PostgresCheckpointer(BaseCheckpointSaver):
    """PostgreSQL-backed checkpointer for langgraph"""

    def __init__(self):
        super().__init__()
        # Create table if it doesn't exist
        Base.metadata.create_all(bind=engine, tables=[CheckpointRecord.__table__])

    def _serialize(self, obj: Any) -> str:
        """Serialize object to JSON string."""
        return json.dumps(obj, default=str)
    
    def _deserialize(self, data: str) -> Any:
        """Deserialize JSON string to object."""
        return json.loads(data) if data else {}

    def get_tuple(self, config: Dict[str, Any]) -> Optional[Tuple[Checkpoint, CheckpointMetadata]]:
        """Get the latest checkpoint for a thread"""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None
        with SessionLocal() as db:
            record = db.query(CheckpointRecord).filter(
                CheckpointRecord.thread_id == thread_id
            ).order_by(
                CheckpointRecord.created_at.desc()
            ).first()

            if not record:
                return None
            
            checkpoint = self._deserialize(record.checkpoint_data)
            metadata = self._deserialize(record.metadata_data)

            return checkpoint, CheckpointMetadata(**metadata)
        
    def put(
            self,
            config: Dict[str, Any],
            checkpoint: Checkpoint,
            metadata: CheckpointMetadata,
            new_versions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Save a checkpoint"""
        thread_id = config.get("configurable", {}).get("thread_id")
        checkpoint_id = checkpoint.get("id", str(uuid.uuid4()))
        parent_id = config.get("configurable", {}).get("checkpoint_id")

        with SessionLocal() as db:
            record = CheckpointRecord(
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                parent_id=parent_id,
                checkpoint_data=self._serialize(checkpoint),
                metadata_data=self._serialize(metadata.__dict__ if hasattr(metadata, '__dict__') else {})
            )
            db.add(record)
            db.commit()
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id
            }
        }

    def put_writes(
            self,
            config: Dict[str, Any],
            writes: list,
            task_id: str,
            task_path: str = ""
    ) -> None:
        """Store intermediate writes linked to a checkpoint.
        
        This is required by newer versions of LangGraph.
        For simple use cases, we can store writes as part of the checkpoint.
        """
        # For now, we don't need to persist intermediate writes separately
        # The checkpoint itself contains the final state
        pass
    
    def list(self, config: Dict[str, Any], *, before: Optional[str] = None, limit: int = 10):
        """List checkpoints for a thread."""
        thread_id = config.get("configurable", {}).get("thread_id")

        with SessionLocal() as db:
            query = db.query(CheckpointRecord).filter(
                CheckpointRecord.thread_id == thread_id
            ).order_by(CheckpointRecord.created_at.desc())

            if limit:
                query = query.limit(limit)

            for record in query.all():
                yield {
                    "checkpoint": self._deserialize(record.checkpoint_data),
                    "metadata": self._deserialize(record.metadata_data),
                    "config": {
                        "configurable": {
                            "thread_id": record.thread_id,
                            "checkpoint_id": record.checkpoint_id
                        }
                    }
                }
