from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

router = APIRouter()


@router.get("/current")
async def get_current_macro():
    # TODO: Implement with real data from Redis cache or database
    return {
        "data": {
            "dxy_value": None,
            "gold_price": None,
            "silver_price": None,
            "m2_supply_trillions": None,
            "fed_funds_rate": None,
            "ten_year_yield": None,
            "cpi_yoy": None,
        },
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/history")
async def get_macro_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    metrics: str = Query("dxy,gold,m2"),
):
    # TODO: Implement historical macro data
    return {"data": []}


@router.get("/dashboard")
async def get_macro_dashboard():
    # TODO: Implement dashboard summary with real data
    return {
        "dxy": {"current": None, "change_1d": None, "change_ytd": None},
        "gold": {"current": None, "change_1d": None, "change_ytd": None},
        "silver": {"current": None, "change_1d": None, "change_ytd": None},
        "m2": {"current": None, "yoy_change": None},
        "rates": {"fed_funds": None, "ten_year": None},
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
