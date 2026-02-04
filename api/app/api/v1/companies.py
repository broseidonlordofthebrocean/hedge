"""Companies API v1 endpoints."""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from sqlalchemy import select, func, or_, desc, asc
from sqlalchemy.orm import joinedload

from ..deps import DBSession
from ...schemas.company import CompanyList, CompanyDetail, CompanySearch
from ...models import Company, SurvivalScore, Fundamental

router = APIRouter()


@router.get("", response_model=CompanyList)
async def list_companies(
    db: DBSession,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    sector: Optional[str] = None,
    min_score: Optional[float] = Query(None, ge=0, le=100),
    max_score: Optional[float] = Query(None, ge=0, le=100),
    tier: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("score", pattern="^(score|ticker|market_cap|name)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
):
    """List companies with filtering and pagination."""
    # Subquery for latest score
    latest_score_subq = (
        select(
            SurvivalScore.company_id,
            func.max(SurvivalScore.score_date).label("max_date"),
        )
        .group_by(SurvivalScore.company_id)
        .subquery()
    )

    # Base query with latest scores
    query = (
        select(Company, SurvivalScore)
        .outerjoin(
            latest_score_subq,
            Company.id == latest_score_subq.c.company_id,
        )
        .outerjoin(
            SurvivalScore,
            (SurvivalScore.company_id == Company.id)
            & (SurvivalScore.score_date == latest_score_subq.c.max_date),
        )
        .where(Company.is_active == True)
    )

    # Apply filters
    if sector:
        query = query.where(Company.sector == sector)

    if min_score is not None:
        query = query.where(SurvivalScore.total_score >= min_score)

    if max_score is not None:
        query = query.where(SurvivalScore.total_score <= max_score)

    if tier:
        query = query.where(SurvivalScore.tier == tier.upper())

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Company.ticker.ilike(search_term),
                Company.name.ilike(search_term),
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting
    sort_func = desc if sort_order == "desc" else asc
    if sort_by == "score":
        query = query.order_by(sort_func(SurvivalScore.total_score))
    elif sort_by == "ticker":
        query = query.order_by(sort_func(Company.ticker))
    elif sort_by == "market_cap":
        query = query.order_by(sort_func(Company.market_cap))
    elif sort_by == "name":
        query = query.order_by(sort_func(Company.name))

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    # Execute query
    result = await db.execute(query)
    rows = result.all()

    # Format response
    companies = []
    for company, score in rows:
        companies.append({
            "id": str(company.id),
            "ticker": company.ticker,
            "name": company.name,
            "sector": company.sector,
            "industry": company.industry,
            "market_cap": company.market_cap,
            "score": float(score.total_score) if score else None,
            "tier": score.tier if score else None,
            "confidence": float(score.confidence) if score and score.confidence else None,
        })

    pages = (total + limit - 1) // limit if total > 0 else 0

    return {
        "data": companies,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages,
        },
    }


@router.get("/search")
async def search_companies(
    db: DBSession,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
):
    """Search companies by ticker or name."""
    search_term = f"%{q}%"

    query = (
        select(Company)
        .where(
            Company.is_active == True,
            or_(
                Company.ticker.ilike(search_term),
                Company.name.ilike(search_term),
            ),
        )
        .order_by(
            # Prioritize exact ticker matches
            Company.ticker.ilike(q).desc(),
            Company.ticker,
        )
        .limit(limit)
    )

    result = await db.execute(query)
    companies = result.scalars().all()

    return {
        "data": [
            {
                "ticker": c.ticker,
                "name": c.name,
                "sector": c.sector,
            }
            for c in companies
        ]
    }


@router.get("/{ticker}", response_model=CompanyDetail)
async def get_company(
    db: DBSession,
    ticker: str,
):
    """Get detailed company information with latest score."""
    # Get company
    query = select(Company).where(Company.ticker == ticker.upper())
    result = await db.execute(query)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")

    # Get latest score
    score_query = (
        select(SurvivalScore)
        .where(SurvivalScore.company_id == company.id)
        .order_by(SurvivalScore.score_date.desc())
        .limit(1)
    )
    score_result = await db.execute(score_query)
    score = score_result.scalar_one_or_none()

    # Get latest fundamental
    fund_query = (
        select(Fundamental)
        .where(Fundamental.company_id == company.id)
        .order_by(Fundamental.fiscal_year.desc())
        .limit(1)
    )
    fund_result = await db.execute(fund_query)
    fundamental = fund_result.scalar_one_or_none()

    return {
        "id": str(company.id),
        "ticker": company.ticker,
        "name": company.name,
        "sector": company.sector,
        "industry": company.industry,
        "market_cap": company.market_cap,
        "country": company.country,
        "exchange": company.exchange,
        "description": company.description,
        "website": company.website,
        "logo_url": company.logo_url,
        "score": {
            "total": float(score.total_score) if score else None,
            "tier": score.tier if score else None,
            "confidence": float(score.confidence) if score and score.confidence else None,
            "date": score.score_date.isoformat() if score else None,
            "factors": {
                "hard_assets": float(score.hard_assets_score) if score and score.hard_assets_score else None,
                "precious_metals": float(score.precious_metals_score) if score and score.precious_metals_score else None,
                "commodities": float(score.commodity_score) if score and score.commodity_score else None,
                "foreign_revenue": float(score.foreign_revenue_score) if score and score.foreign_revenue_score else None,
                "pricing_power": float(score.pricing_power_score) if score and score.pricing_power_score else None,
                "debt_structure": float(score.debt_structure_score) if score and score.debt_structure_score else None,
                "essential_services": float(score.essential_services_score) if score and score.essential_services_score else None,
            },
            "scenarios": {
                "gradual": float(score.scenario_gradual) if score and score.scenario_gradual else None,
                "rapid": float(score.scenario_rapid) if score and score.scenario_rapid else None,
                "hyper": float(score.scenario_hyper) if score and score.scenario_hyper else None,
            },
        } if score else None,
        "fundamentals": {
            "total_assets": float(fundamental.total_assets) if fundamental and fundamental.total_assets else None,
            "total_revenue": float(fundamental.total_revenue) if fundamental and fundamental.total_revenue else None,
            "total_debt": float(fundamental.total_debt) if fundamental and fundamental.total_debt else None,
            "gross_margin": float(fundamental.gross_margin) if fundamental and fundamental.gross_margin else None,
            "foreign_revenue_pct": float(fundamental.foreign_revenue_pct) if fundamental and fundamental.foreign_revenue_pct else None,
            "fiscal_year": fundamental.fiscal_year if fundamental else None,
        } if fundamental else None,
    }


@router.get("/{ticker}/scores")
async def get_company_scores(
    db: DBSession,
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(30, ge=1, le=365),
):
    """Get score history for a company."""
    from datetime import date

    # Get company
    company_query = select(Company).where(Company.ticker == ticker.upper())
    company_result = await db.execute(company_query)
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")

    # Build score query
    query = (
        select(SurvivalScore)
        .where(SurvivalScore.company_id == company.id)
    )

    if start_date:
        query = query.where(SurvivalScore.score_date >= date.fromisoformat(start_date))

    if end_date:
        query = query.where(SurvivalScore.score_date <= date.fromisoformat(end_date))

    query = query.order_by(SurvivalScore.score_date.desc()).limit(limit)

    result = await db.execute(query)
    scores = result.scalars().all()

    return {
        "data": [
            {
                "date": s.score_date.isoformat(),
                "total_score": float(s.total_score),
                "tier": s.tier,
                "confidence": float(s.confidence) if s.confidence else None,
                "factors": {
                    "hard_assets": float(s.hard_assets_score) if s.hard_assets_score else None,
                    "precious_metals": float(s.precious_metals_score) if s.precious_metals_score else None,
                    "commodities": float(s.commodity_score) if s.commodity_score else None,
                    "foreign_revenue": float(s.foreign_revenue_score) if s.foreign_revenue_score else None,
                    "pricing_power": float(s.pricing_power_score) if s.pricing_power_score else None,
                    "debt_structure": float(s.debt_structure_score) if s.debt_structure_score else None,
                    "essential_services": float(s.essential_services_score) if s.essential_services_score else None,
                },
                "scenarios": {
                    "gradual": float(s.scenario_gradual) if s.scenario_gradual else None,
                    "rapid": float(s.scenario_rapid) if s.scenario_rapid else None,
                    "hyper": float(s.scenario_hyper) if s.scenario_hyper else None,
                },
            }
            for s in scores
        ]
    }


@router.get("/{ticker}/fundamentals")
async def get_company_fundamentals(
    db: DBSession,
    ticker: str,
    years: int = Query(5, ge=1, le=10),
):
    """Get fundamental data history for a company."""
    # Get company
    company_query = select(Company).where(Company.ticker == ticker.upper())
    company_result = await db.execute(company_query)
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")

    # Get fundamentals
    query = (
        select(Fundamental)
        .where(Fundamental.company_id == company.id)
        .order_by(Fundamental.fiscal_year.desc())
        .limit(years)
    )

    result = await db.execute(query)
    fundamentals = result.scalars().all()

    return {
        "data": [
            {
                "fiscal_year": f.fiscal_year,
                "total_assets": float(f.total_assets) if f.total_assets else None,
                "tangible_assets": float(f.tangible_assets) if f.tangible_assets else None,
                "total_revenue": float(f.total_revenue) if f.total_revenue else None,
                "total_debt": float(f.total_debt) if f.total_debt else None,
                "gross_margin": float(f.gross_margin) if f.gross_margin else None,
                "foreign_revenue_pct": float(f.foreign_revenue_pct) if f.foreign_revenue_pct else None,
                "commodity_revenue_pct": float(f.commodity_revenue_pct) if f.commodity_revenue_pct else None,
            }
            for f in fundamentals
        ]
    }


@router.get("/{ticker}/peers")
async def get_company_peers(
    db: DBSession,
    ticker: str,
):
    """Get peer companies in the same sector."""
    # Get company
    company_query = select(Company).where(Company.ticker == ticker.upper())
    company_result = await db.execute(company_query)
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")

    # Get peers with latest scores
    latest_score_subq = (
        select(
            SurvivalScore.company_id,
            func.max(SurvivalScore.score_date).label("max_date"),
        )
        .group_by(SurvivalScore.company_id)
        .subquery()
    )

    query = (
        select(Company, SurvivalScore)
        .outerjoin(
            latest_score_subq,
            Company.id == latest_score_subq.c.company_id,
        )
        .outerjoin(
            SurvivalScore,
            (SurvivalScore.company_id == Company.id)
            & (SurvivalScore.score_date == latest_score_subq.c.max_date),
        )
        .where(
            Company.is_active == True,
            Company.sector == company.sector,
            Company.ticker != ticker.upper(),
        )
        .order_by(SurvivalScore.total_score.desc())
        .limit(10)
    )

    result = await db.execute(query)
    peers = result.all()

    return {
        "data": [
            {
                "ticker": peer.ticker,
                "name": peer.name,
                "sector": peer.sector,
                "industry": peer.industry,
                "score": float(score.total_score) if score else None,
                "tier": score.tier if score else None,
            }
            for peer, score in peers
        ]
    }
