"""
SEC EDGAR API integration service.

Provides async methods to fetch company filings, documents, and search
for companies via the SEC EDGAR API.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class RateLimiter:
    """
    Simple rate limiter to respect SEC's 10 requests/second limit.
    """

    def __init__(self, max_requests: int = 10, window_seconds: float = 1.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: list[datetime] = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a request slot is available."""
        async with self._lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.window_seconds)

            # Remove old requests outside the window
            self.requests = [r for r in self.requests if r > cutoff]

            if len(self.requests) >= self.max_requests:
                # Calculate wait time until oldest request expires
                oldest = min(self.requests)
                wait_time = (oldest + timedelta(seconds=self.window_seconds) - now).total_seconds()
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.3f}s")
                    await asyncio.sleep(wait_time)
                    # Clean up again after waiting
                    now = datetime.now()
                    cutoff = now - timedelta(seconds=self.window_seconds)
                    self.requests = [r for r in self.requests if r > cutoff]

            self.requests.append(datetime.now())


class SECEdgarError(Exception):
    """Base exception for SEC EDGAR API errors."""

    pass


class SECEdgarRateLimitError(SECEdgarError):
    """Raised when SEC rate limit is exceeded."""

    pass


class SECEdgarNotFoundError(SECEdgarError):
    """Raised when a resource is not found."""

    pass


class SECEdgarService:
    """
    Async service for interacting with the SEC EDGAR API.

    Handles rate limiting, proper User-Agent headers, and provides methods
    for fetching company filings and documents.
    """

    BASE_URL = "https://data.sec.gov"
    EFTS_URL = "https://efts.sec.gov/LATEST/search-index"
    COMPANY_SEARCH_URL = "https://www.sec.gov/cgi-bin/browse-edgar"

    def __init__(self, user_agent: str | None = None):
        """
        Initialize the SEC EDGAR service.

        Args:
            user_agent: User-Agent string for SEC requests. SEC requires
                        a valid contact email in the User-Agent.
        """
        self.user_agent = user_agent or settings.sec_user_agent
        if not self.user_agent:
            raise SECEdgarError(
                "SEC User-Agent is required. Set sec_user_agent in config or pass to constructor."
            )

        self.rate_limiter = RateLimiter(max_requests=10, window_seconds=1.0)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "SECEdgarService":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(30.0),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, raising if not initialized."""
        if self._client is None:
            raise SECEdgarError(
                "SECEdgarService must be used as an async context manager. "
                "Use 'async with SECEdgarService() as service:'"
            )
        return self._client

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        """
        Make a rate-limited request to SEC.

        Args:
            method: HTTP method
            url: Full URL to request
            **kwargs: Additional arguments passed to httpx

        Returns:
            httpx.Response object

        Raises:
            SECEdgarRateLimitError: If rate limited by SEC
            SECEdgarNotFoundError: If resource not found
            SECEdgarError: For other HTTP errors
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.request(method, url, **kwargs)

            if response.status_code == 429:
                logger.warning("SEC rate limit exceeded (429 response)")
                raise SECEdgarRateLimitError("SEC rate limit exceeded. Please wait and retry.")

            if response.status_code == 404:
                raise SECEdgarNotFoundError(f"Resource not found: {url}")

            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            logger.error(f"SEC API HTTP error: {e.response.status_code} for {url}")
            raise SECEdgarError(f"SEC API error: {e.response.status_code}") from e

        except httpx.RequestError as e:
            logger.error(f"SEC API request error: {e}")
            raise SECEdgarError(f"SEC API request failed: {e}") from e

    @staticmethod
    def normalize_cik(cik: str | int) -> str:
        """
        Normalize CIK to 10-digit zero-padded string.

        Args:
            cik: Company CIK number (with or without leading zeros)

        Returns:
            10-digit zero-padded CIK string
        """
        return str(cik).lstrip("0").zfill(10)

    async def get_company_filings(
        self,
        cik: str | int,
        filing_type: str = "10-K",
        count: int = 40,
    ) -> list[dict[str, Any]]:
        """
        Get recent filings for a company.

        Args:
            cik: Company CIK number
            filing_type: Filing type to filter (e.g., "10-K", "10-Q", "8-K")
            count: Maximum number of filings to return

        Returns:
            List of filing dictionaries with keys:
                - accessionNumber: Filing accession number
                - filingDate: Date filed
                - reportDate: Report period end date
                - form: Filing form type
                - primaryDocument: Primary document filename
                - primaryDocDescription: Document description
        """
        normalized_cik = self.normalize_cik(cik)
        url = f"{self.BASE_URL}/submissions/CIK{normalized_cik}.json"

        logger.info(f"Fetching filings for CIK {normalized_cik}, type={filing_type}")

        response = await self._request("GET", url)
        data = response.json()

        # Extract recent filings from the submissions data
        filings = []
        recent = data.get("filings", {}).get("recent", {})

        if not recent:
            logger.warning(f"No filings found for CIK {normalized_cik}")
            return []

        # Build list of filings
        forms = recent.get("form", [])
        accession_numbers = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])
        primary_documents = recent.get("primaryDocument", [])
        primary_doc_descriptions = recent.get("primaryDocDescription", [])

        for i in range(len(forms)):
            form = forms[i] if i < len(forms) else ""

            # Filter by filing type if specified
            if filing_type and form != filing_type:
                continue

            filing = {
                "accessionNumber": accession_numbers[i] if i < len(accession_numbers) else "",
                "filingDate": filing_dates[i] if i < len(filing_dates) else "",
                "reportDate": report_dates[i] if i < len(report_dates) else "",
                "form": form,
                "primaryDocument": primary_documents[i] if i < len(primary_documents) else "",
                "primaryDocDescription": (
                    primary_doc_descriptions[i] if i < len(primary_doc_descriptions) else ""
                ),
                "cik": normalized_cik,
            }
            filings.append(filing)

            if len(filings) >= count:
                break

        logger.info(f"Found {len(filings)} {filing_type} filings for CIK {normalized_cik}")
        return filings

    async def get_filing_document(
        self,
        accession_number: str,
        cik: str | int | None = None,
        document_name: str | None = None,
    ) -> str:
        """
        Download a filing document.

        Args:
            accession_number: Filing accession number (e.g., "0000320193-23-000077")
            cik: Company CIK (required to construct URL)
            document_name: Specific document to download. If None, fetches the
                          filing index to find the primary document.

        Returns:
            Document content as string (HTML/XBRL)

        Raises:
            SECEdgarError: If CIK is not provided
            SECEdgarNotFoundError: If document not found
        """
        if cik is None:
            raise SECEdgarError("CIK is required to fetch filing document")

        normalized_cik = self.normalize_cik(cik)
        # Remove dashes from accession number for URL path
        accession_no_dashes = accession_number.replace("-", "")

        if document_name:
            # Direct document download
            url = (
                f"{self.BASE_URL}/Archives/edgar/data/"
                f"{normalized_cik.lstrip('0')}/{accession_no_dashes}/{document_name}"
            )
            logger.info(f"Fetching document: {document_name}")
        else:
            # Fetch filing index to find primary document
            index_url = (
                f"{self.BASE_URL}/Archives/edgar/data/"
                f"{normalized_cik.lstrip('0')}/{accession_no_dashes}/index.json"
            )

            logger.info(f"Fetching filing index for accession {accession_number}")
            index_response = await self._request("GET", index_url)
            index_data = index_response.json()

            # Find primary document (usually the main HTML file)
            primary_doc = None
            for item in index_data.get("directory", {}).get("item", []):
                name = item.get("name", "")
                if name.endswith(".htm") and not name.startswith("R"):
                    # Prefer files that look like the main document
                    if "10-k" in name.lower() or "10k" in name.lower():
                        primary_doc = name
                        break
                    if primary_doc is None:
                        primary_doc = name

            if not primary_doc:
                raise SECEdgarNotFoundError(
                    f"Could not find primary document in filing {accession_number}"
                )

            url = (
                f"{self.BASE_URL}/Archives/edgar/data/"
                f"{normalized_cik.lstrip('0')}/{accession_no_dashes}/{primary_doc}"
            )
            logger.info(f"Fetching primary document: {primary_doc}")

        response = await self._request("GET", url)
        return response.text

    async def search_company(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search for companies by name or ticker.

        Args:
            query: Search query (company name or ticker symbol)
            limit: Maximum number of results to return

        Returns:
            List of company dictionaries with keys:
                - cik: Company CIK number
                - name: Company name
                - ticker: Stock ticker (if available)
        """
        # Use the company tickers JSON file for fast lookups
        url = f"{self.BASE_URL}/files/company_tickers.json"

        logger.info(f"Searching companies for query: {query}")

        response = await self._request("GET", url)
        data = response.json()

        query_lower = query.lower().strip()
        results = []

        # Search through all companies
        for entry in data.values():
            cik = str(entry.get("cik_str", ""))
            name = entry.get("title", "")
            ticker = entry.get("ticker", "")

            # Match against ticker or name
            if (
                query_lower == ticker.lower()
                or query_lower in name.lower()
                or query_lower == cik.lstrip("0")
            ):
                results.append(
                    {
                        "cik": self.normalize_cik(cik),
                        "name": name,
                        "ticker": ticker,
                    }
                )

                if len(results) >= limit:
                    break

        # Sort by relevance (exact ticker match first)
        results.sort(
            key=lambda x: (
                0 if x["ticker"].lower() == query_lower else 1,
                x["name"].lower(),
            )
        )

        logger.info(f"Found {len(results)} companies matching '{query}'")
        return results

    async def get_company_info(self, cik: str | int) -> dict[str, Any]:
        """
        Get detailed company information.

        Args:
            cik: Company CIK number

        Returns:
            Dictionary with company details including:
                - cik: Normalized CIK
                - name: Company name
                - sic: SIC code
                - sicDescription: SIC description
                - tickers: List of ticker symbols
                - exchanges: List of exchanges
                - fiscalYearEnd: Fiscal year end month/day
        """
        normalized_cik = self.normalize_cik(cik)
        url = f"{self.BASE_URL}/submissions/CIK{normalized_cik}.json"

        logger.info(f"Fetching company info for CIK {normalized_cik}")

        response = await self._request("GET", url)
        data = response.json()

        return {
            "cik": normalized_cik,
            "name": data.get("name", ""),
            "sic": data.get("sic", ""),
            "sicDescription": data.get("sicDescription", ""),
            "tickers": data.get("tickers", []),
            "exchanges": data.get("exchanges", []),
            "fiscalYearEnd": data.get("fiscalYearEnd", ""),
            "stateOfIncorporation": data.get("stateOfIncorporation", ""),
            "ein": data.get("ein", ""),
        }
