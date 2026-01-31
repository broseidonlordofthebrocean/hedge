from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class WatchlistItemCreate(BaseModel):
    ticker: str
    notes: Optional[str] = None


@router.get("")
async def list_watchlist():
    # TODO: Implement with auth and database
    return {"data": []}


@router.post("")
async def add_to_watchlist(item: WatchlistItemCreate):
    # TODO: Implement watchlist addition
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{company_id}")
async def remove_from_watchlist(company_id: str):
    # TODO: Implement watchlist removal
    return {"success": True}
