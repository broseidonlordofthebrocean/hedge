from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ScreenerFilters(BaseModel):
    sectors: Optional[list[str]] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    min_market_cap: Optional[int] = None
    max_market_cap: Optional[int] = None
    min_foreign_revenue_pct: Optional[float] = None
    min_hard_assets_score: Optional[float] = None
    min_precious_metals_score: Optional[float] = None
    has_dividend: Optional[bool] = None
    countries: Optional[list[str]] = None


class ScreenerRequest(BaseModel):
    filters: ScreenerFilters
    sort_by: str = "total_score"
    sort_order: str = "desc"
    page: int = 1
    limit: int = 50


@router.post("")
async def run_screener(request: ScreenerRequest):
    # TODO: Implement screener with filters
    return {
        "data": [],
        "pagination": {
            "page": request.page,
            "limit": request.limit,
            "total": 0,
            "pages": 0,
        },
        "filter_summary": {
            "matched": 0,
            "total_universe": 0,
        }
    }


@router.get("/presets")
async def get_screener_presets():
    return {
        "data": [
            {
                "id": "gold_bugs",
                "name": "Gold Bugs",
                "description": "Companies with high precious metals exposure",
                "filters": {
                    "min_precious_metals_score": 70,
                }
            },
            {
                "id": "inflation_hedge",
                "name": "Inflation Hedges",
                "description": "Strong pricing power and hard asset backing",
                "filters": {
                    "min_hard_assets_score": 60,
                    "min_score": 70,
                }
            },
            {
                "id": "global_revenue",
                "name": "Global Revenue",
                "description": "High foreign revenue exposure",
                "filters": {
                    "min_foreign_revenue_pct": 50,
                }
            },
            {
                "id": "commodity_plays",
                "name": "Commodity Plays",
                "description": "Oil, gas, and mining companies",
                "filters": {
                    "sectors": ["Oil & Gas E&P", "Oil & Gas Integrated", "Gold Mining", "Diversified Mining", "Copper Mining"],
                }
            },
        ]
    }
