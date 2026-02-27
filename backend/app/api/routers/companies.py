from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Company, ESGScore, ESGEvent
from app.core.auth import get_current_user, TokenPayload
from app.schemas.common import CompanyOut, ESGScoreOut, ESGEventOut

router = APIRouter(prefix="/v1/companies", tags=["companies"])


def parse_range(range_str: str) -> timedelta:
    if range_str.endswith("d"):
        return timedelta(days=int(range_str[:-1]))
    elif range_str.endswith("h"):
        return timedelta(hours=int(range_str[:-1]))
    return timedelta(days=30)


@router.get("", response_model=list[CompanyOut])
async def list_companies(
    query: Optional[str] = Query(None),
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Company).where(Company.tenant_id == current_user.tenant_id)
    if query:
        stmt = stmt.where(Company.name.ilike(f"%{query}%"))
    stmt = stmt.order_by(Company.name).limit(100)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(
    company_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(
            Company.id == company_id,
            Company.tenant_id == current_user.tenant_id,
        )
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/{company_id}/scores", response_model=list[ESGScoreOut])
async def get_scores(
    company_id: str,
    range: str = Query("30d"),
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - parse_range(range)
    result = await db.execute(
        select(ESGScore)
        .where(
            ESGScore.company_id == company_id,
            ESGScore.tenant_id == current_user.tenant_id,
            ESGScore.recorded_at >= since,
        )
        .order_by(ESGScore.recorded_at.asc())
    )
    return result.scalars().all()


@router.get("/{company_id}/events", response_model=list[ESGEventOut])
async def get_events(
    company_id: str,
    range: str = Query("30d"),
    severity_gte: Optional[int] = Query(None),
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - parse_range(range)
    stmt = select(ESGEvent).where(
        ESGEvent.company_id == company_id,
        ESGEvent.tenant_id == current_user.tenant_id,
        ESGEvent.event_date >= since,
    )
    if severity_gte is not None:
        stmt = stmt.where(ESGEvent.severity >= severity_gte)
    stmt = stmt.order_by(ESGEvent.event_date.desc()).limit(200)
    result = await db.execute(stmt)
    return result.scalars().all()
