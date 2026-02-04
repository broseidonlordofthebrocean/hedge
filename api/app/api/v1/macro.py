"""Macro data API v1 endpoints."""

from fastapi import APIRouter, Query, Depends
from typing import Optional
from datetime import datetime, date, timedelta
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...models import MacroData

router = APIRouter()


@router.get("/current")
async def get_current_macro(
    db: AsyncSession = Depends(get_db),
):
    """Get current macro data."""
    # Get latest macro data
    query = select(MacroData).order_by(desc(MacroData.data_date)).limit(1)
    result = await db.execute(query)
    macro = result.scalar_one_or_none()

    if not macro:
        return {
            "data": None,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }

    return {
        "data": {
            "date": macro.data_date.isoformat(),
            "dxy_value": float(macro.dxy_value) if macro.dxy_value else None,
            "dxy_change_1d": float(macro.dxy_change_1d) if macro.dxy_change_1d else None,
            "dxy_change_ytd": float(macro.dxy_change_ytd) if macro.dxy_change_ytd else None,
            "gold_price": float(macro.gold_price) if macro.gold_price else None,
            "silver_price": float(macro.silver_price) if macro.silver_price else None,
            "platinum_price": float(macro.platinum_price) if macro.platinum_price else None,
            "oil_wti_price": float(macro.oil_wti_price) if macro.oil_wti_price else None,
            "copper_price": float(macro.copper_price) if macro.copper_price else None,
            "m2_supply_trillions": float(macro.m2_supply_trillions) if macro.m2_supply_trillions else None,
            "m2_yoy_change": float(macro.m2_yoy_change) if macro.m2_yoy_change else None,
            "fed_funds_rate": float(macro.fed_funds_rate) if macro.fed_funds_rate else None,
            "ten_year_yield": float(macro.ten_year_yield) if macro.ten_year_yield else None,
            "cpi_yoy": float(macro.cpi_yoy) if macro.cpi_yoy else None,
            "pce_yoy": float(macro.pce_yoy) if macro.pce_yoy else None,
            "eur_usd": float(macro.eur_usd) if macro.eur_usd else None,
            "usd_jpy": float(macro.usd_jpy) if macro.usd_jpy else None,
            "gbp_usd": float(macro.gbp_usd) if macro.gbp_usd else None,
            "usd_cny": float(macro.usd_cny) if macro.usd_cny else None,
        },
        "updated_at": macro.created_at if macro.created_at else datetime.utcnow().isoformat() + "Z",
    }


@router.get("/history")
async def get_macro_history(
    db: AsyncSession = Depends(get_db),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    metrics: str = Query("dxy,gold,m2"),
    limit: int = Query(90, ge=1, le=365),
):
    """Get historical macro data."""
    query = select(MacroData)

    if start_date:
        query = query.where(MacroData.data_date >= date.fromisoformat(start_date))
    else:
        # Default to last 90 days
        query = query.where(MacroData.data_date >= date.today() - timedelta(days=90))

    if end_date:
        query = query.where(MacroData.data_date <= date.fromisoformat(end_date))

    query = query.order_by(MacroData.data_date.asc()).limit(limit)

    result = await db.execute(query)
    rows = result.scalars().all()

    # Parse requested metrics
    requested_metrics = [m.strip().lower() for m in metrics.split(",")]

    data = []
    for row in rows:
        point = {"date": row.data_date.isoformat()}

        if "dxy" in requested_metrics:
            point["dxy"] = float(row.dxy_value) if row.dxy_value else None

        if "gold" in requested_metrics:
            point["gold"] = float(row.gold_price) if row.gold_price else None

        if "silver" in requested_metrics:
            point["silver"] = float(row.silver_price) if row.silver_price else None

        if "m2" in requested_metrics:
            point["m2"] = float(row.m2_supply_trillions) if row.m2_supply_trillions else None

        if "oil" in requested_metrics:
            point["oil"] = float(row.oil_wti_price) if row.oil_wti_price else None

        if "rates" in requested_metrics:
            point["fed_funds"] = float(row.fed_funds_rate) if row.fed_funds_rate else None
            point["ten_year"] = float(row.ten_year_yield) if row.ten_year_yield else None

        if "inflation" in requested_metrics:
            point["cpi"] = float(row.cpi_yoy) if row.cpi_yoy else None
            point["pce"] = float(row.pce_yoy) if row.pce_yoy else None

        data.append(point)

    return {"data": data}


@router.get("/dashboard")
async def get_macro_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """Get macro dashboard summary with changes."""
    # Get latest data
    latest_query = select(MacroData).order_by(desc(MacroData.data_date)).limit(1)
    latest_result = await db.execute(latest_query)
    latest = latest_result.scalar_one_or_none()

    # Get data from 1 day ago
    yesterday_query = (
        select(MacroData)
        .where(MacroData.data_date < date.today())
        .order_by(desc(MacroData.data_date))
        .limit(1)
    )
    yesterday_result = await db.execute(yesterday_query)
    yesterday = yesterday_result.scalar_one_or_none()

    # Get YTD data (first day of year)
    ytd_query = (
        select(MacroData)
        .where(MacroData.data_date >= date(date.today().year, 1, 1))
        .order_by(MacroData.data_date.asc())
        .limit(1)
    )
    ytd_result = await db.execute(ytd_query)
    ytd_start = ytd_result.scalar_one_or_none()

    def calc_change(current, previous):
        if current is None or previous is None or float(previous) == 0:
            return None
        return round((float(current) - float(previous)) / float(previous) * 100, 2)

    if not latest:
        return {
            "dxy": {"current": None, "change_1d": None, "change_ytd": None},
            "gold": {"current": None, "change_1d": None, "change_ytd": None},
            "silver": {"current": None, "change_1d": None, "change_ytd": None},
            "m2": {"current": None, "yoy_change": None},
            "rates": {"fed_funds": None, "ten_year": None},
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }

    return {
        "dxy": {
            "current": float(latest.dxy_value) if latest.dxy_value else None,
            "change_1d": calc_change(latest.dxy_value, yesterday.dxy_value if yesterday else None),
            "change_ytd": calc_change(latest.dxy_value, ytd_start.dxy_value if ytd_start else None),
        },
        "gold": {
            "current": float(latest.gold_price) if latest.gold_price else None,
            "change_1d": calc_change(latest.gold_price, yesterday.gold_price if yesterday else None),
            "change_ytd": calc_change(latest.gold_price, ytd_start.gold_price if ytd_start else None),
        },
        "silver": {
            "current": float(latest.silver_price) if latest.silver_price else None,
            "change_1d": calc_change(latest.silver_price, yesterday.silver_price if yesterday else None),
            "change_ytd": calc_change(latest.silver_price, ytd_start.silver_price if ytd_start else None),
        },
        "oil": {
            "current": float(latest.oil_wti_price) if latest.oil_wti_price else None,
            "change_1d": calc_change(latest.oil_wti_price, yesterday.oil_wti_price if yesterday else None),
            "change_ytd": calc_change(latest.oil_wti_price, ytd_start.oil_wti_price if ytd_start else None),
        },
        "m2": {
            "current": float(latest.m2_supply_trillions) if latest.m2_supply_trillions else None,
            "yoy_change": float(latest.m2_yoy_change) if latest.m2_yoy_change else None,
        },
        "rates": {
            "fed_funds": float(latest.fed_funds_rate) if latest.fed_funds_rate else None,
            "ten_year": float(latest.ten_year_yield) if latest.ten_year_yield else None,
        },
        "inflation": {
            "cpi_yoy": float(latest.cpi_yoy) if latest.cpi_yoy else None,
            "pce_yoy": float(latest.pce_yoy) if latest.pce_yoy else None,
        },
        "currencies": {
            "eur_usd": float(latest.eur_usd) if latest.eur_usd else None,
            "usd_jpy": float(latest.usd_jpy) if latest.usd_jpy else None,
            "gbp_usd": float(latest.gbp_usd) if latest.gbp_usd else None,
            "usd_cny": float(latest.usd_cny) if latest.usd_cny else None,
        },
        "updated_at": latest.created_at if latest.created_at else datetime.utcnow().isoformat() + "Z",
    }
