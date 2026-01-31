from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from ..deps import DBSession
from ...schemas.company import CompanyList, CompanyDetail, CompanySearch

router = APIRouter()


@router.get("", response_model=CompanyList)
async def list_companies(
    db: DBSession,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    sector: Optional[str] = None,
    min_score: Optional[float] = Query(None, ge=0, le=100),
    max_score: Optional[float] = Query(None, ge=0, le=100),
    search: Optional[str] = None,
    sort_by: str = Query("score", pattern="^(score|ticker|market_cap|name)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
):
    # TODO: Implement with database query
    return {
        "data": [],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": 0,
            "pages": 0,
        }
    }


@router.get("/search")
async def search_companies(
    db: DBSession,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
):
    # TODO: Implement search
    return {"data": []}


@router.get("/{ticker}", response_model=CompanyDetail)
async def get_company(
    db: DBSession,
    ticker: str,
):
    # TODO: Implement with database query
    raise HTTPException(status_code=404, detail=f"Company {ticker} not found")


@router.get("/{ticker}/scores")
async def get_company_scores(
    db: DBSession,
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(30, ge=1, le=365),
):
    # TODO: Implement score history
    return {"data": []}


@router.get("/{ticker}/fundamentals")
async def get_company_fundamentals(
    db: DBSession,
    ticker: str,
    years: int = Query(5, ge=1, le=10),
):
    # TODO: Implement fundamentals history
    return {"data": []}


@router.get("/{ticker}/peers")
async def get_company_peers(
    db: DBSession,
    ticker: str,
):
    # TODO: Implement peer comparison
    return {"data": []}
