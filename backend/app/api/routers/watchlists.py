from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Watchlist, WatchlistItem
from app.core.auth import get_current_user, TokenPayload
from app.schemas.common import WatchlistOut, WatchlistCreate, WatchlistItemCreate

router = APIRouter(prefix="/v1/watchlists", tags=["watchlists"])


@router.get("", response_model=list[WatchlistOut])
async def list_watchlists(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.tenant_id == current_user.tenant_id,
            Watchlist.user_id == current_user.sub,
        )
    )
    return result.scalars().all()


@router.post("", response_model=WatchlistOut)
async def create_watchlist(
    body: WatchlistCreate,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wl = Watchlist(
        tenant_id=current_user.tenant_id,
        user_id=current_user.sub,
        name=body.name,
    )
    db.add(wl)
    await db.flush()
    await db.refresh(wl, ["items"])
    return wl


@router.get("/{watchlist_id}", response_model=WatchlistOut)
async def get_watchlist(
    watchlist_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.id == watchlist_id,
            Watchlist.tenant_id == current_user.tenant_id,
        )
    )
    wl = result.scalar_one_or_none()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return wl


@router.post("/{watchlist_id}/items")
async def add_item(
    watchlist_id: str,
    body: WatchlistItemCreate,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.id == watchlist_id,
            Watchlist.tenant_id == current_user.tenant_id,
        )
    )
    wl = result.scalar_one_or_none()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    item = WatchlistItem(watchlist_id=watchlist_id, company_id=body.company_id)
    db.add(item)
    await db.flush()
    return {"status": "added", "id": item.id}


@router.delete("/{watchlist_id}/items/{company_id}")
async def remove_item(
    watchlist_id: str,
    company_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.company_id == company_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
    return {"status": "removed"}
