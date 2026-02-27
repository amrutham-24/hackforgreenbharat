from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CompanyOut(BaseModel):
    id: str
    name: str
    ticker: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = ""
    logo_url: Optional[str] = ""

    model_config = {"from_attributes": True}


class ESGScoreOut(BaseModel):
    id: str
    company_id: str
    overall: float
    environmental: float
    social: float
    governance: float
    risk_level: str
    recorded_at: datetime

    model_config = {"from_attributes": True}


class ESGEventOut(BaseModel):
    id: str
    company_id: str
    title: str
    description: Optional[str] = ""
    source_url: Optional[str] = ""
    category: str
    subcategory: Optional[str] = ""
    severity: int
    confidence: float
    sentiment: str
    event_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class WatchlistOut(BaseModel):
    id: str
    name: str
    created_at: datetime
    items: List["WatchlistItemOut"] = []

    model_config = {"from_attributes": True}


class WatchlistItemOut(BaseModel):
    id: str
    company_id: str
    added_at: datetime

    model_config = {"from_attributes": True}


class WatchlistCreate(BaseModel):
    name: str


class WatchlistItemCreate(BaseModel):
    company_id: str


class AlertRuleCreate(BaseModel):
    name: str
    company_id: Optional[str] = None
    condition_type: str  # score_drop, severity_gte, category_match
    threshold: float = 0
    category_filter: Optional[str] = ""
    channels: List[str] = ["email"]


class AlertRuleOut(BaseModel):
    id: str
    name: str
    company_id: Optional[str] = None
    condition_type: str
    threshold: float
    category_filter: Optional[str] = ""
    channels: list
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertDeliveryOut(BaseModel):
    id: str
    rule_id: str
    event_id: Optional[str] = None
    channel: str
    status: str
    payload: dict
    delivered_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    message: str
    company_id: Optional[str] = None


class Citation(BaseModel):
    idx: int
    title: str
    url: str
    ts: Optional[datetime] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation] = []
    used_company_id: Optional[str] = None


class IngestEventRequest(BaseModel):
    company_id: str
    title: str
    description: str
    source_url: Optional[str] = ""
    category: Optional[str] = ""
    raw_text: Optional[str] = ""
    event_date: Optional[datetime] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    email: str
    full_name: str


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}
