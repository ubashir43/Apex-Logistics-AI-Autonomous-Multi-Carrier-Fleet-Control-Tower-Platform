"""
Conversation Model - Chat sessions between customers and the AI/agents
FRD v3.0 — Tenant-scoped conversations with widget session support
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import secrets

from app.database import Base


class ConversationStatus(str, enum.Enum):
    """Conversation status enumeration"""
    ACTIVE = "active"
    PENDING = "pending"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Conversation(Base):
    """
    Conversation model representing a chat session.
    Tracks sentiment, escalation status, and message history.
    Scoped to a tenant (FR-7.3).
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    # Tenant Isolation (FR-7.3)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    tenant = relationship("Tenant", back_populates="conversations")

    # Widget Session (FR-6.2.14)
    session_id = Column(String(100), unique=True, index=True, nullable=True)

    # Customer Reference
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer = relationship("User", back_populates="conversations", foreign_keys=[customer_id])

    # Customer Info from pre-chat form (FR-6.2.1)
    customer_name = Column(String(100), nullable=True)
    customer_email = Column(String(255), nullable=True)

    # Status
    status = Column(String(20), default=ConversationStatus.ACTIVE.value)
    priority = Column(String(20), default="normal")  # low, normal, high, urgent

    # Sentiment Tracking
    current_sentiment = Column(String(20), default="neutral")  # positive, neutral, negative
    sentiment_score = Column(Float, default=0.5)  # 0.0 to 1.0
    frustration_level = Column(Float, default=0.0)  # 0.0 to 1.0

    # Escalation
    is_escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Language
    detected_language = Column(String(10), default="en")
    language_name = Column(String(50), default="English")
    language_flag = Column(String(10), default="🇺🇸")

    # Summary
    last_message_preview = Column(String(200), nullable=True)
    message_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    escalations = relationship("Escalation", back_populates="conversation", cascade="all, delete-orphan")

    @staticmethod
    def generate_session_id() -> str:
        """Generate a unique session ID for widget chat sessions"""
        return f"sess_{secrets.token_urlsafe(24)}"

    def to_dict(self) -> dict:
        """Serialize conversation details to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name or "Anonymous Shipper",
            "customer_email": self.customer_email,
            "status": self.status,
            "priority": self.priority,
            "current_sentiment": self.current_sentiment,
            "sentiment_score": self.sentiment_score,
            "frustration_level": self.frustration_level,
            "is_escalated": self.is_escalated,
            "escalation_reason": self.escalation_reason,
            "escalated_at": self.escalated_at.isoformat() if self.escalated_at else None,
            "assigned_agent_id": self.assigned_agent_id,
            "detected_language": self.detected_language,
            "language_name": self.language_name,
            "language_flag": self.language_flag,
            "last_message_preview": self.last_message_preview,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Conversation {self.id} - {self.status}>"
