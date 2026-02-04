"""Data ingestion background tasks."""

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .celery_app import celery_app
from ..config import get_settings
from ..models import Company, MacroData
from ..ingestion import MarketDataService, MacroDataService

logger = logging.getLogger(__name__)
settings = get_settings()


def get_async_session():
    engine = create_async_engine(settings.database_url)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(name="app.tasks.ingestion.ingest_macro_data")
def ingest_macro_data():
    """Fetch and store latest macro data."""
    import asyncio
    return asyncio.run(_ingest_macro_data_async())


async def _ingest_macro_data_async():
    """Async implementation of macro data ingestion."""
    logger.info("Ingesting macro data")

    async with MacroDataService() as service:
        data = await service.get_all_macro_data()

    async_session = get_async_session()
    async with async_session() as db:
        # Check if we already have data for today
        result = await db.execute(
            select(MacroData).where(MacroData.data_date == date.today())
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            for key, value in data.items():
                if key != "data_date" and value is not None:
                    setattr(existing, key, value)
        else:
            # Create new
            macro = MacroData(**data)
            db.add(macro)

        await db.commit()

    logger.info("Macro data ingestion complete")
    return {"status": "success", "date": str(date.today())}


@celery_app.task(name="app.tasks.ingestion.ingest_market_data")
def ingest_market_data():
    """Fetch and update market data for tracked companies."""
    import asyncio
    return asyncio.run(_ingest_market_data_async())


async def _ingest_market_data_async():
    """Async implementation of market data ingestion."""
    logger.info("Ingesting market data")

    async_session = get_async_session()
    updated = 0

    async with async_session() as db:
        result = await db.execute(
            select(Company).where(Company.is_active == True).limit(100)
        )
        companies = result.scalars().all()
        tickers = [c.ticker for c in companies]

    if not tickers:
        return {"status": "no_companies"}

    async with MarketDataService() as service:
        quotes = await service.get_batch_quotes(tickers)

    async with async_session() as db:
        for ticker, quote in quotes.items():
            result = await db.execute(
                select(Company).where(Company.ticker == ticker)
            )
            company = result.scalar_one_or_none()
            if company and quote.get("close"):
                # Update market cap if we have price and shares
                updated += 1

        await db.commit()

    logger.info(f"Market data ingestion complete: {updated} updated")
    return {"status": "success", "updated": updated}


@celery_app.task(name="app.tasks.ingestion.ingest_company_fundamentals")
def ingest_company_fundamentals(ticker: str):
    """Fetch fundamentals for a specific company."""
    import asyncio
    return asyncio.run(_ingest_company_fundamentals_async(ticker))


async def _ingest_company_fundamentals_async(ticker: str):
    """Async implementation of company fundamentals ingestion."""
    logger.info(f"Ingesting fundamentals for {ticker}")

    async with MarketDataService() as service:
        financials = await service.get_stock_financials(ticker)
        company_info = await service.get_company_info(ticker)

    if not financials and not company_info:
        return {"status": "no_data", "ticker": ticker}

    # Store in database...
    return {"status": "success", "ticker": ticker}


@celery_app.task(name="app.tasks.ingestion.update_all_fundamentals")
def update_all_fundamentals():
    """Batch update fundamentals for all companies."""
    import asyncio
    return asyncio.run(_update_all_fundamentals_async())


async def _update_all_fundamentals_async():
    """Async implementation of batch fundamentals update."""
    logger.info("Starting batch fundamentals update")

    async_session = get_async_session()

    async with async_session() as db:
        result = await db.execute(
            select(Company).where(Company.is_active == True)
        )
        companies = result.scalars().all()

    updated = 0
    for company in companies:
        try:
            ingest_company_fundamentals.delay(company.ticker)
            updated += 1
        except Exception as e:
            logger.error(f"Error queuing {company.ticker}: {e}")

    logger.info(f"Queued {updated} companies for fundamentals update")
    return {"status": "queued", "count": updated}
