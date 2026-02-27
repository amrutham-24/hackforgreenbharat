from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Company, ESGScore
from app.core.auth import get_current_user, TokenPayload
from app.schemas.common import ChatRequest, ChatResponse
from app.services.rag import query_similar, generate_chat_answer

router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = body.company_id
    if not company_id:
        result = await db.execute(
            select(Company)
            .where(Company.tenant_id == current_user.tenant_id)
            .limit(1)
        )
        company = result.scalar_one_or_none()
        if company:
            company_id = company.id
        else:
            raise HTTPException(status_code=400, detail="No company_id provided and no companies found")

    result = await db.execute(
        select(Company).where(
            Company.id == company_id,
            Company.tenant_id == current_user.tenant_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Company not found")

    evidence = await query_similar(
        query=body.message,
        tenant_id=current_user.tenant_id,
        company_id=company_id,
        top_k=5,
    )

    answer_data = await generate_chat_answer(
        query=body.message,
        evidence_docs=evidence,
        db=db,
        company_id=company_id,
        tenant_id=current_user.tenant_id,
    )

    return ChatResponse(**answer_data)
