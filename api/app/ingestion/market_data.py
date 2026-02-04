"""Market data ingestion from Polygon.io and fallback sources."""

import httpx
import logging
from typing import Optional, Any
from decimal import Decimal

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MarketDataService:
    """Service for fetching market data from external APIs."""

    POLYGON_BASE_URL = "https://api.polygon.io"

    def __init__(self):
        self.api_key = settings.polygon_api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "MarketDataService":
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("MarketDataService must be used as async context manager")
        return self._client

    async def get_stock_quote(self, ticker: str) -> Optional[dict[str, Any]]:
        """Get current stock quote from Polygon."""
        if not self.api_key:
            logger.warning("Polygon API key not configured")
            return None

        try:
            url = f"{self.POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/prev"
            response = await self.client.get(url, params={"apiKey": self.api_key})
            response.raise_for_status()
            data = response.json()

            if data.get("results"):
                result = data["results"][0]
                return {
                    "ticker": ticker,
                    "open": Decimal(str(result.get("o", 0))),
                    "high": Decimal(str(result.get("h", 0))),
                    "low": Decimal(str(result.get("l", 0))),
                    "close": Decimal(str(result.get("c", 0))),
                    "volume": result.get("v", 0),
                    "vwap": Decimal(str(result.get("vw", 0))),
                }
            return None
        except httpx.HTTPError as e:
            logger.error(f"Error fetching quote for {ticker}: {e}")
            return None

    async def get_company_info(self, ticker: str) -> Optional[dict[str, Any]]:
        """Get company details from Polygon."""
        if not self.api_key:
            return None

        try:
            url = f"{self.POLYGON_BASE_URL}/v3/reference/tickers/{ticker}"
            response = await self.client.get(url, params={"apiKey": self.api_key})
            response.raise_for_status()
            data = response.json()

            if data.get("results"):
                result = data["results"]
                return {
                    "ticker": result.get("ticker"),
                    "name": result.get("name"),
                    "market_cap": result.get("market_cap"),
                    "sector": result.get("sic_description"),
                    "industry": result.get("sic_description"),
                    "description": result.get("description"),
                    "homepage_url": result.get("homepage_url"),
                    "logo_url": result.get("branding", {}).get("logo_url"),
                    "exchange": result.get("primary_exchange"),
                    "cik": result.get("cik"),
                }
            return None
        except httpx.HTTPError as e:
            logger.error(f"Error fetching company info for {ticker}: {e}")
            return None

    async def get_stock_financials(self, ticker: str) -> Optional[dict[str, Any]]:
        """Get financial data from Polygon."""
        if not self.api_key:
            return None

        try:
            url = f"{self.POLYGON_BASE_URL}/vX/reference/financials"
            response = await self.client.get(
                url,
                params={"ticker": ticker, "limit": 1, "apiKey": self.api_key},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("results"):
                result = data["results"][0]
                financials = result.get("financials", {})
                balance_sheet = financials.get("balance_sheet", {})
                income = financials.get("income_statement", {})

                return {
                    "fiscal_year": result.get("fiscal_year"),
                    "fiscal_period": result.get("fiscal_period"),
                    "total_assets": balance_sheet.get("assets", {}).get("value"),
                    "total_liabilities": balance_sheet.get("liabilities", {}).get("value"),
                    "total_equity": balance_sheet.get("equity", {}).get("value"),
                    "total_revenue": income.get("revenues", {}).get("value"),
                    "gross_profit": income.get("gross_profit", {}).get("value"),
                    "operating_income": income.get("operating_income_loss", {}).get("value"),
                    "net_income": income.get("net_income_loss", {}).get("value"),
                }
            return None
        except httpx.HTTPError as e:
            logger.error(f"Error fetching financials for {ticker}: {e}")
            return None

    async def get_batch_quotes(self, tickers: list[str]) -> dict[str, dict]:
        """Get quotes for multiple tickers."""
        results = {}
        for ticker in tickers:
            quote = await self.get_stock_quote(ticker)
            if quote:
                results[ticker] = quote
        return results
