"""Rankings API v1 endpoints."""

from fastapi import APIRouter, Query, Depends
from typing import Optional
from datetime import datetime, timedelta, date
from sqlalchemy import select, func, desc, asc, case
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...models import Company, SurvivalScore

router = APIRouter()

# Tier definitions
TIERS = {
    "FORTRESS": {"min": 80, "max": 100},
    "RESILIENT": {"min": 65, "max": 79.99},
    "MODERATE": {"min": 50, "max": 64.99},
    "VULNERABLE": {"min": 35, "max": 49.99},
    "EXPOSED": {"min": 0, "max": 34.99},
}


@router.get("")
async def get_rankings(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sector: Optional[str] = None,
    tier: Optional[str] = None,
    scenario: str = Query("current", pattern="^(current|gradual|rapid|hyper)$"),
):
    """Get ranked companies by survival score."""
    # Subquery for latest score
    latest_score_subq = (
        select(
            SurvivalScore.company_id,
            func.max(SurvivalScore.score_date).label("max_date"),
        )
        .group_by(SurvivalScore.company_id)
        .subquery()
    )

    # Build main query
    query = (
        select(Company, SurvivalScore)
        .join(
            latest_score_subq,
            Company.id == latest_score_subq.c.company_id,
        )
        .join(
            SurvivalScore,
            (SurvivalScore.company_id == Company.id)
            & (SurvivalScore.score_date == latest_score_subq.c.max_date),
        )
        .where(Company.is_active == True)
    )

    # Apply filters
    if sector:
        query = query.where(Company.sector == sector)

    if tier:
        tier_upper = tier.upper()
        if tier_upper in TIERS:
            query = query.where(SurvivalScore.tier == tier_upper)

    # Determine sort column based on scenario
    if scenario == "gradual":
        sort_col = SurvivalScore.scenario_gradual
    elif scenario == "rapid":
        sort_col = SurvivalScore.scenario_rapid
    elif scenario == "hyper":
        sort_col = SurvivalScore.scenario_hyper
    else:
        sort_col = SurvivalScore.total_score

    query = query.order_by(desc(sort_col)).offset(offset).limit(limit)

    # Execute query
    result = await db.execute(query)
    rows = result.all()

    # Count total
    count_query = (
        select(func.count(Company.id))
        .join(
            latest_score_subq,
            Company.id == latest_score_subq.c.company_id,
        )
        .where(Company.is_active == True)
    )
    if sector:
        count_query = count_query.where(Company.sector == sector)
    if tier:
        count_query = count_query.where(SurvivalScore.tier == tier.upper())

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Format response
    rankings = []
    for rank, (company, score) in enumerate(rows, start=offset + 1):
        score_value = (
            float(getattr(score, f"scenario_{scenario}"))
            if scenario != "current"
            else float(score.total_score)
        )
        rankings.append({
            "rank": rank,
            "ticker": company.ticker,
            "name": company.name,
            "sector": company.sector,
            "industry": company.industry,
            "score": score_value,
            "tier": score.tier,
            "confidence": float(score.confidence) if score.confidence else None,
            "factors": {
                "hard_assets": float(score.hard_assets_score) if score.hard_assets_score else None,
                "precious_metals": float(score.precious_metals_score) if score.precious_metals_score else None,
                "commodities": float(score.commodity_score) if score.commodity_score else None,
                "foreign_revenue": float(score.foreign_revenue_score) if score.foreign_revenue_score else None,
                "pricing_power": float(score.pricing_power_score) if score.pricing_power_score else None,
                "debt_structure": float(score.debt_structure_score) if score.debt_structure_score else None,
                "essential_services": float(score.essential_services_score) if score.essential_services_score else None,
            },
        })

    return {
        "data": rankings,
        "total": total,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/sectors")
async def get_sector_rankings(
    db: AsyncSession = Depends(get_db),
):
    """Get average scores by sector."""
    # Subquery for latest score
    latest_score_subq = (
        select(
            SurvivalScore.company_id,
            func.max(SurvivalScore.score_date).label("max_date"),
        )
        .group_by(SurvivalScore.company_id)
        .subquery()
    )

    # Aggregate by sector
    query = (
        select(
            Company.sector,
            func.count(Company.id).label("count"),
            func.avg(SurvivalScore.total_score).label("avg_score"),
            func.min(SurvivalScore.total_score).label("min_score"),
            func.max(SurvivalScore.total_score).label("max_score"),
        )
        .join(
            latest_score_subq,
            Company.id == latest_score_subq.c.company_id,
        )
        .join(
            SurvivalScore,
            (SurvivalScore.company_id == Company.id)
            & (SurvivalScore.score_date == latest_score_subq.c.max_date),
        )
        .where(Company.is_active == True)
        .group_by(Company.sector)
        .order_by(desc(func.avg(SurvivalScore.total_score)))
    )

    result = await db.execute(query)
    rows = result.all()

    return {
        "data": [
            {
                "sector": row.sector,
                "count": row.count,
                "avg_score": round(float(row.avg_score), 2) if row.avg_score else None,
                "min_score": round(float(row.min_score), 2) if row.min_score else None,
                "max_score": round(float(row.max_score), 2) if row.max_score else None,
            }
            for row in rows
            if row.sector
        ]
    }


@router.get("/movers")
async def get_score_movers(
    db: AsyncSession = Depends(get_db),
    period: str = Query("1d", pattern="^(1d|7d|30d)$"),
    limit: int = Query(10, ge=1, le=50),
):
    """Get companies with biggest score changes."""
    # Calculate date range
    days = {"1d": 1, "7d": 7, "30d": 30}[period]
    compare_date = date.today() - timedelta(days=days)

    # Get current scores
    current_score_subq = (
        select(
            SurvivalScore.company_id,
            func.max(SurvivalScore.score_date).label("max_date"),
        )
        .group_by(SurvivalScore.company_id)
        .subquery()
    )

    # Get historical scores
    historical_score_subq = (
        select(
            SurvivalScore.company_id,
            SurvivalScore.total_score.label("old_score"),
        )
        .where(SurvivalScore.score_date <= compare_date)
        .distinct(SurvivalScore.company_id)
        .order_by(SurvivalScore.company_id, SurvivalScore.score_date.desc())
        .subquery()
    )

    # Calculate changes
    query = (
        select(
            Company,
            SurvivalScore.total_score.label("current_score"),
            historical_score_subq.c.old_score,
            (SurvivalScore.total_score - historical_score_subq.c.old_score).label("change"),
        )
        .join(
            current_score_subq,
            Company.id == current_score_subq.c.company_id,
        )
        .join(
            SurvivalScore,
            (SurvivalScore.company_id == Company.id)
            & (SurvivalScore.score_date == current_score_subq.c.max_date),
        )
        .join(
            historical_score_subq,
            Company.id == historical_score_subq.c.company_id,
        )
        .where(Company.is_active == True)
    )

    # Get gainers
    gainers_query = query.order_by(
        desc(SurvivalScore.total_score - historical_score_subq.c.old_score)
    ).limit(limit)

    gainers_result = await db.execute(gainers_query)
    gainers = gainers_result.all()

    # Get losers
    losers_query = query.order_by(
        asc(SurvivalScore.total_score - historical_score_subq.c.old_score)
    ).limit(limit)

    losers_result = await db.execute(losers_query)
    losers = losers_result.all()

    def format_mover(row):
        return {
            "ticker": row.Company.ticker,
            "name": row.Company.name,
            "sector": row.Company.sector,
            "current_score": round(float(row.current_score), 2),
            "previous_score": round(float(row.old_score), 2),
            "change": round(float(row.change), 2),
            "change_pct": round(float(row.change) / float(row.old_score) * 100, 2) if row.old_score else 0,
        }

    return {
        "period": period,
        "gainers": [format_mover(r) for r in gainers if r.change and r.change > 0],
        "losers": [format_mover(r) for r in losers if r.change and r.change < 0],
    }


@router.get("/tiers")
async def get_tier_distribution(
    db: AsyncSession = Depends(get_db),
):
    """Get distribution of companies across tiers."""
    # Subquery for latest score
    latest_score_subq = (
        select(
            SurvivalScore.company_id,
            func.max(SurvivalScore.score_date).label("max_date"),
        )
        .group_by(SurvivalScore.company_id)
        .subquery()
    )

    # Count by tier
    query = (
        select(
            SurvivalScore.tier,
            func.count(SurvivalScore.id).label("count"),
            func.avg(SurvivalScore.total_score).label("avg_score"),
        )
        .join(
            latest_score_subq,
            (SurvivalScore.company_id == latest_score_subq.c.company_id)
            & (SurvivalScore.score_date == latest_score_subq.c.max_date),
        )
        .join(Company, Company.id == SurvivalScore.company_id)
        .where(Company.is_active == True)
        .group_by(SurvivalScore.tier)
    )

    result = await db.execute(query)
    rows = result.all()

    tier_counts = {row.tier: {"count": row.count, "avg": float(row.avg_score) if row.avg_score else None} for row in rows}

    return {
        "FORTRESS": {
            "min": TIERS["FORTRESS"]["min"],
            "max": TIERS["FORTRESS"]["max"],
            "count": tier_counts.get("FORTRESS", {}).get("count", 0),
            "avg_score": tier_counts.get("FORTRESS", {}).get("avg"),
        },
        "RESILIENT": {
            "min": TIERS["RESILIENT"]["min"],
            "max": TIERS["RESILIENT"]["max"],
            "count": tier_counts.get("RESILIENT", {}).get("count", 0),
            "avg_score": tier_counts.get("RESILIENT", {}).get("avg"),
        },
        "MODERATE": {
            "min": TIERS["MODERATE"]["min"],
            "max": TIERS["MODERATE"]["max"],
            "count": tier_counts.get("MODERATE", {}).get("count", 0),
            "avg_score": tier_counts.get("MODERATE", {}).get("avg"),
        },
        "VULNERABLE": {
            "min": TIERS["VULNERABLE"]["min"],
            "max": TIERS["VULNERABLE"]["max"],
            "count": tier_counts.get("VULNERABLE", {}).get("count", 0),
            "avg_score": tier_counts.get("VULNERABLE", {}).get("avg"),
        },
        "EXPOSED": {
            "min": TIERS["EXPOSED"]["min"],
            "max": TIERS["EXPOSED"]["max"],
            "count": tier_counts.get("EXPOSED", {}).get("count", 0),
            "avg_score": tier_counts.get("EXPOSED", {}).get("avg"),
        },
    }
