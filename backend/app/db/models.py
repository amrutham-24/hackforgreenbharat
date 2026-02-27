import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Text, Boolean,
    ForeignKey, Index, JSON, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


def utcnow():
    return datetime.now(timezone.utc)


def new_uuid():
    return str(uuid.uuid4())


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    users = relationship("User", back_populates="tenant")


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    tenant_id = Column(UUID(as_uuid=False), ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), default="")
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    tenant = relationship("Tenant", back_populates="users")

    __table_args__ = (Index("ix_users_tenant", "tenant_id"),)


class Company(Base):
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    tenant_id = Column(UUID(as_uuid=False), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    ticker = Column(String(20))
    sector = Column(String(100))
    country = Column(String(100))
    description = Column(Text, default="")
    logo_url = Column(String(500), default="")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    scores = relationship("ESGScore", back_populates="company", order_by="desc(ESGScore.recorded_at)")
    events = relationship("ESGEvent", back_populates="company", order_by="desc(ESGEvent.event_date)")

    __table_args__ = (Index("ix_companies_tenant", "tenant_id"),)


class ESGScore(Base):
    __tablename__ = "esg_scores"
    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    tenant_id = Column(UUID(as_uuid=False), ForeignKey("tenants.id"), nullable=False)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    overall = Column(Float, nullable=False)
    environmental = Column(Float, nullable=False)
    social = Column(Float, nullable=False)
    governance = Column(Float, nullable=False)
    risk_level = Column(String(20), default="medium")
    recorded_at = Column(DateTime(timezone=True), default=utcnow)

    company = relationship("Company", back_populates="scores")

    __table_args__ = (
        Index("ix_esg_scores_company_time", "company_id", "recorded_at"),
        Index("ix_esg_scores_tenant", "tenant_id"),
    )


class ESGEvent(Base):
    __tablename__ = "esg_events"
    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    tenant_id = Column(UUID(as_uuid=False), ForeignKey("tenants.id"), nullable=False)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    source_url = Column(String(1000), default="")
    category = Column(String(50), nullable=False)  # environmental, social, governance
    subcategory = Column(String(100), default="")
    severity = Column(Integer, default=5)  # 1-10
    confidence = Column(Float, default=0.8)
    sentiment = Column(String(20), default="negative")
    event_date = Column(DateTime(timezone=True), default=utcnow)
    raw_text = Column(Text, default="")
    classification_json = Column(JSON, default=dict)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    company = relationship("Company", back_populates="events")

    __table_args__ = (
        Index("ix_esg_events_company_date", "company_id", "event_date"),
        Index("ix_esg_events_tenant", "tenant_id"),
        Index("ix_esg_events_severity", "severity"),
    )


class RAGDocument(Base):
    __tablename__ = "rag_documents"
    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    tenant_id = Column(UUID(as_uuid=False), ForeignKey("tenants.id"), nullable=False)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    event_id = Column(UUID(as_uuid=False), ForeignKey("esg_events.id"), nullable=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source_url = Column(String(1000), default="")
    embedding_id = Column(String(255), default="")
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (Index("ix_rag_docs_tenant_company", "tenant_id", "company_id"),)


class Watchlist(Base):
    __tablename__ = "watchlists"
    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    tenant_id = Column(UUID(as_uuid=False), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_watchlists_user", "user_id", "tenant_id"),)


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    watchlist_id = Column(UUID(as_uuid=False), ForeignKey("watchlists.id"), nullable=False)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), default=utcnow)

    watchlist = relationship("Watchlist", back_populates="items")

    __table_args__ = (Index("ix_watchlist_items_wl", "watchlist_id"),)


class AlertRule(Base):
    __tablename__ = "alert_rules"
    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    tenant_id = Column(UUID(as_uuid=False), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=True)
    condition_type = Column(String(50), nullable=False)  # score_drop, severity_gte, category_match
    threshold = Column(Float, default=0)
    category_filter = Column(String(50), default="")
    channels = Column(JSON, default=list)  # ["slack", "email"]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (Index("ix_alert_rules_tenant", "tenant_id"),)


class AlertDelivery(Base):
    __tablename__ = "alert_deliveries"
    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    tenant_id = Column(UUID(as_uuid=False), ForeignKey("tenants.id"), nullable=False)
    rule_id = Column(UUID(as_uuid=False), ForeignKey("alert_rules.id"), nullable=False)
    event_id = Column(UUID(as_uuid=False), ForeignKey("esg_events.id"), nullable=True)
    channel = Column(String(50), nullable=False)
    status = Column(String(50), default="sent")
    payload = Column(JSON, default=dict)
    delivered_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (Index("ix_alert_deliveries_tenant", "tenant_id"),)
