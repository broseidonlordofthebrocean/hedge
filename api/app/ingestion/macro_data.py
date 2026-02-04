"""Macro data ingestion from FRED and other sources."""

import httpx
import logging
from typing import Optional, Any
from decimal import Decimal
from datetime import date

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MacroDataService:
    """Service for fetching macroeconomic data."""

    FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    SERIES = {
        "dxy": "DTWEXBGS",
        "m2": "M2SL",
        "fed_funds": "FEDFUNDS",
        "cpi": "CPIAUCSL",
        "ten_year": "GS10",
        "pce": "PCEPI",
    }

    def __init__(self):
        self.api_key = settings.fred_api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "MacroDataService":
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("MacroDataService must be used as async context manager")
        return self._client

    async def _fetch_fred_series(self, series_id: str, limit: int = 1) -> Optional[Decimal]:
        """Fetch latest value from FRED."""
        if not self.api_key:
            logger.warning("FRED API key not configured")
            return None

        try:
            response = await self.client.get(
                self.FRED_BASE_URL,
                params={
                    "series_id": series_id,
                    "api_key": self.api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": limit,
                },
            )
            response.raise_for_status()
            data = response.json()

            observations = data.get("observations", [])
            if observations:
                value = observations[0].get("value")
                if value and value != ".":
                    return Decimal(value)
            return None
        except httpx.HTTPError as e:
            logger.error(f"Error fetching FRED series {series_id}: {e}")
            return None

    async def get_dxy(self) -> Optional[Decimal]:
        return await self._fetch_fred_series(self.SERIES["dxy"])

    async def get_m2(self) -> Optional[Decimal]:
        return await self._fetch_fred_series(self.SERIES["m2"])

    async def get_fed_funds(self) -> Optional[Decimal]:
        return await self._fetch_fred_series(self.SERIES["fed_funds"])

    async def get_cpi(self) -> Optional[Decimal]:
        return await self._fetch_fred_series(self.SERIES["cpi"])

    async def get_treasury_yield(self) -> Optional[Decimal]:
        return await self._fetch_fred_series(self.SERIES["ten_year"])

    async def get_precious_metals(self) -> dict[str, Optional[Decimal]]:
        """Get gold and silver prices."""
        try:
            response = await self.client.get(
                "https://api.metals.dev/v1/latest",
                params={"api_key": "demo", "currency": "USD", "unit": "toz"},
            )
            if response.status_code == 200:
                data = response.json()
                metals = data.get("metals", {})
                return {
                    "gold": Decimal(str(metals.get("gold", 0))) if metals.get("gold") else None,
                    "silver": Decimal(str(metals.get("silver", 0))) if metals.get("silver") else None,
                    "platinum": Decimal(str(metals.get("platinum", 0))) if metals.get("platinum") else None,
                }
        except Exception as e:
            logger.error(f"Error fetching precious metals: {e}")
        return {"gold": None, "silver": None, "platinum": None}

    async def get_all_macro_data(self) -> dict[str, Any]:
        """Fetch all macro indicators."""
        metals = await self.get_precious_metals()
        return {
            "data_date": date.today(),
            "dxy_value": await self.get_dxy(),
            "gold_price": metals.get("gold"),
            "silver_price": metals.get("silver"),
            "platinum_price": metals.get("platinum"),
            "m2_supply_trillions": await self.get_m2(),
            "fed_funds_rate": await self.get_fed_funds(),
            "ten_year_yield": await self.get_treasury_yield(),
            "cpi_yoy": await self.get_cpi(),
        }
