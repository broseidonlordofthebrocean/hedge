"""Scoring background tasks."""

import logging
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .celery_app import celery_app
from ..config import get_settings
from ..models import Company, SurvivalScore, Fundamental, ScoringRun
from ..services.scoring import ScoringEngine
from ..services.scoring.factors import CompanyData

logger = logging.getLogger(__name__)
settings = get_settings()


def get_async_session():
    engine = create_async_engine(settings.database_url)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(bind=True, name="app.tasks.scoring.run_daily_scoring")
def run_daily_scoring(self):
    """Run daily scoring for all active companies."""
    import asyncio
    return asyncio.run(_run_daily_scoring_async())


async def _run_daily_scoring_async():
    """Async implementation of daily scoring."""
    logger.info("Starting daily scoring run")

    async_session = get_async_session()
    engine = ScoringEngine()
    today = date.today()

    scored = 0
    failed = 0
    scores = []

    async with async_session() as db:
        # Create scoring run record
        scoring_run = ScoringRun(
            run_date=today,
            status="running",
            scoring_version=engine.VERSION,
        )
        db.add(scoring_run)
        await db.commit()

        # Get all active companies
        result = await db.execute(
            select(Company).where(Company.is_active == True)
        )
        companies = result.scalars().all()

        for company in companies:
            try:
                # Get latest fundamentals
                fund_result = await db.execute(
                    select(Fundamental)
                    .where(Fundamental.company_id == company.id)
                    .order_by(Fundamental.fiscal_year.desc())
                    .limit(1)
                )
                fundamental = fund_result.scalar_one_or_none()

                # Build CompanyData
                company_data = CompanyData(
                    ticker=company.ticker,
                    sector=company.sector,
                    industry=company.industry,
                )

                if fundamental:
                    company_data.total_assets = fundamental.total_assets
                    company_data.tangible_assets = fundamental.tangible_assets
                    company_data.total_revenue = fundamental.total_revenue
                    company_data.foreign_revenue_pct = fundamental.foreign_revenue_pct
                    company_data.gross_margin = fundamental.gross_margin
                    company_data.gross_margin_5yr_std = fundamental.gross_margin_5yr_std
                    company_data.total_debt = fundamental.total_debt
                    company_data.fixed_rate_debt_pct = fundamental.fixed_rate_debt_pct
                    company_data.avg_debt_maturity_years = fundamental.avg_debt_maturity_years
                    company_data.commodity_revenue_pct = fundamental.commodity_revenue_pct
                    company_data.precious_metals_revenue_pct = fundamental.precious_metals_revenue_pct
                    company_data.proven_reserves_oz = fundamental.proven_reserves_oz

                # Score company
                result = engine.score(company_data)

                # Save score
                score = SurvivalScore(
                    company_id=company.id,
                    score_date=today,
                    total_score=result.total_score,
                    confidence=result.confidence,
                    tier=result.tier,
                    hard_assets_score=result.factors["hard_assets"],
                    precious_metals_score=result.factors["precious_metals"],
                    commodity_score=result.factors["commodities"],
                    foreign_revenue_score=result.factors["foreign_revenue"],
                    pricing_power_score=result.factors["pricing_power"],
                    debt_structure_score=result.factors["debt_structure"],
                    essential_services_score=result.factors["essential_services"],
                    scenario_gradual=result.scenario_scores["gradual"],
                    scenario_rapid=result.scenario_scores["rapid"],
                    scenario_hyper=result.scenario_scores["hyper"],
                    scoring_version=engine.VERSION,
                )
                db.add(score)
                scores.append(float(result.total_score))
                scored += 1

            except Exception as e:
                logger.error(f"Error scoring {company.ticker}: {e}")
                failed += 1

        # Update scoring run
        scoring_run.status = "completed"
        scoring_run.companies_scored = scored
        scoring_run.companies_failed = failed
        if scores:
            scoring_run.avg_score = Decimal(str(sum(scores) / len(scores)))
            sorted_scores = sorted(scores)
            mid = len(sorted_scores) // 2
            scoring_run.median_score = Decimal(str(sorted_scores[mid]))

        await db.commit()

    logger.info(f"Scoring complete: {scored} scored, {failed} failed")
    return {"scored": scored, "failed": failed}


@celery_app.task(name="app.tasks.scoring.score_single_company")
def score_single_company(company_id: str):
    """Score a single company."""
    import asyncio
    return asyncio.run(_score_single_company_async(company_id))


async def _score_single_company_async(company_id: str):
    """Async implementation of single company scoring."""
    async_session = get_async_session()
    engine = ScoringEngine()
    today = date.today()

    async with async_session() as db:
        result = await db.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()

        if not company:
            return {"error": "Company not found"}

        # Similar scoring logic as above...
        company_data = CompanyData(
            ticker=company.ticker,
            sector=company.sector,
            industry=company.industry,
        )

        result = engine.score(company_data)

        score = SurvivalScore(
            company_id=company.id,
            score_date=today,
            total_score=result.total_score,
            confidence=result.confidence,
            tier=result.tier,
            hard_assets_score=result.factors["hard_assets"],
            precious_metals_score=result.factors["precious_metals"],
            commodity_score=result.factors["commodities"],
            foreign_revenue_score=result.factors["foreign_revenue"],
            pricing_power_score=result.factors["pricing_power"],
            debt_structure_score=result.factors["debt_structure"],
            essential_services_score=result.factors["essential_services"],
            scenario_gradual=result.scenario_scores["gradual"],
            scenario_rapid=result.scenario_scores["rapid"],
            scenario_hyper=result.scenario_scores["hyper"],
            scoring_version=engine.VERSION,
        )
        db.add(score)
        await db.commit()

    return {"ticker": company.ticker, "score": float(result.total_score)}
