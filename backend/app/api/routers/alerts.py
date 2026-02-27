from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import AlertRule, AlertDelivery
from app.core.auth import get_current_user, TokenPayload
from app.schemas.common import AlertRuleCreate, AlertRuleOut, AlertDeliveryOut

router = APIRouter(prefix="/v1/alerts", tags=["alerts"])


@router.post("/rules", response_model=AlertRuleOut)
async def create_rule(
    body: AlertRuleCreate,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rule = AlertRule(
        tenant_id=current_user.tenant_id,
        user_id=current_user.sub,
        name=body.name,
        company_id=body.company_id,
        condition_type=body.condition_type,
        threshold=body.threshold,
        category_filter=body.category_filter or "",
        channels=body.channels,
    )
    db.add(rule)
    await db.flush()
    return rule


@router.get("/rules", response_model=list[AlertRuleOut])
async def list_rules(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AlertRule).where(AlertRule.tenant_id == current_user.tenant_id)
    )
    return result.scalars().all()


@router.get("/deliveries", response_model=list[AlertDeliveryOut])
async def list_deliveries(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AlertDelivery)
        .where(AlertDelivery.tenant_id == current_user.tenant_id)
        .order_by(AlertDelivery.delivered_at.desc())
        .limit(100)
    )
    return result.scalars().all()
