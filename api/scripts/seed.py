"""
Seed script for populating the database with initial data.
Run with: python scripts/seed.py
"""

import asyncio
from datetime import date, timedelta
from decimal import Decimal
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import get_settings
from app.database import Base
from app.models import Company, SurvivalScore, Fundamental, MacroData
from app.services.scoring import ScoringEngine
from app.services.scoring.factors import CompanyData

settings = get_settings()

# Sample companies data
COMPANIES = [
    # Excellent tier - Gold/Precious Metals
    {"ticker": "NEM", "name": "Newmont Corporation", "sector": "Materials", "industry": "Gold Mining", "market_cap": 45_000_000_000, "exchange": "NYSE"},
    {"ticker": "GOLD", "name": "Barrick Gold Corporation", "sector": "Materials", "industry": "Gold Mining", "market_cap": 35_000_000_000, "exchange": "NYSE"},
    {"ticker": "AEM", "name": "Agnico Eagle Mines", "sector": "Materials", "industry": "Gold Mining", "market_cap": 30_000_000_000, "exchange": "NYSE"},
    {"ticker": "FNV", "name": "Franco-Nevada Corporation", "sector": "Materials", "industry": "Precious Metals Royalties", "market_cap": 25_000_000_000, "exchange": "NYSE"},
    {"ticker": "WPM", "name": "Wheaton Precious Metals", "sector": "Materials", "industry": "Precious Metals Royalties", "market_cap": 20_000_000_000, "exchange": "NYSE"},

    # Strong tier - Commodities/Energy
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Oil & Gas Integrated", "market_cap": 450_000_000_000, "exchange": "NYSE"},
    {"ticker": "CVX", "name": "Chevron Corporation", "sector": "Energy", "industry": "Oil & Gas Integrated", "market_cap": 280_000_000_000, "exchange": "NYSE"},
    {"ticker": "FCX", "name": "Freeport-McMoRan Inc", "sector": "Materials", "industry": "Copper Mining", "market_cap": 55_000_000_000, "exchange": "NYSE"},
    {"ticker": "RIO", "name": "Rio Tinto Group", "sector": "Materials", "industry": "Diversified Mining", "market_cap": 120_000_000_000, "exchange": "NYSE"},
    {"ticker": "BHP", "name": "BHP Group Limited", "sector": "Materials", "industry": "Diversified Mining", "market_cap": 150_000_000_000, "exchange": "NYSE"},
    {"ticker": "CAT", "name": "Caterpillar Inc", "sector": "Industrials", "industry": "Construction Machinery", "market_cap": 180_000_000_000, "exchange": "NYSE"},
    {"ticker": "DE", "name": "Deere & Company", "sector": "Industrials", "industry": "Agricultural Machinery", "market_cap": 120_000_000_000, "exchange": "NYSE"},

    # Moderate tier - Consumer Staples / Healthcare
    {"ticker": "PG", "name": "Procter & Gamble", "sector": "Consumer Staples", "industry": "Household Products", "market_cap": 380_000_000_000, "exchange": "NYSE"},
    {"ticker": "KO", "name": "The Coca-Cola Company", "sector": "Consumer Staples", "industry": "Beverages", "market_cap": 260_000_000_000, "exchange": "NYSE"},
    {"ticker": "PEP", "name": "PepsiCo Inc", "sector": "Consumer Staples", "industry": "Beverages", "market_cap": 230_000_000_000, "exchange": "NASDAQ"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Pharmaceuticals", "market_cap": 400_000_000_000, "exchange": "NYSE"},
    {"ticker": "MRK", "name": "Merck & Co Inc", "sector": "Healthcare", "industry": "Pharmaceuticals", "market_cap": 280_000_000_000, "exchange": "NYSE"},
    {"ticker": "UNH", "name": "UnitedHealth Group", "sector": "Healthcare", "industry": "Healthcare Facilities", "market_cap": 500_000_000_000, "exchange": "NYSE"},

    # Utilities
    {"ticker": "NEE", "name": "NextEra Energy", "sector": "Utilities", "industry": "Electric Utilities", "market_cap": 150_000_000_000, "exchange": "NYSE"},
    {"ticker": "DUK", "name": "Duke Energy", "sector": "Utilities", "industry": "Electric Utilities", "market_cap": 80_000_000_000, "exchange": "NYSE"},
    {"ticker": "SO", "name": "Southern Company", "sector": "Utilities", "industry": "Electric Utilities", "market_cap": 85_000_000_000, "exchange": "NYSE"},

    # Vulnerable tier - Financials
    {"ticker": "JPM", "name": "JPMorgan Chase & Co", "sector": "Financials", "industry": "Banks", "market_cap": 550_000_000_000, "exchange": "NYSE"},
    {"ticker": "BAC", "name": "Bank of America", "sector": "Financials", "industry": "Banks", "market_cap": 300_000_000_000, "exchange": "NYSE"},
    {"ticker": "WFC", "name": "Wells Fargo & Company", "sector": "Financials", "industry": "Banks", "market_cap": 200_000_000_000, "exchange": "NYSE"},
    {"ticker": "C", "name": "Citigroup Inc", "sector": "Financials", "industry": "Banks", "market_cap": 120_000_000_000, "exchange": "NYSE"},
    {"ticker": "GS", "name": "Goldman Sachs", "sector": "Financials", "industry": "Asset Management", "market_cap": 150_000_000_000, "exchange": "NYSE"},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Financials", "industry": "Asset Management", "market_cap": 160_000_000_000, "exchange": "NYSE"},
    {"ticker": "BLK", "name": "BlackRock Inc", "sector": "Financials", "industry": "Asset Management", "market_cap": 120_000_000_000, "exchange": "NYSE"},

    # Critical tier - Tech/Software (low hard assets)
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software", "market_cap": 3_000_000_000_000, "exchange": "NASDAQ"},
    {"ticker": "AAPL", "name": "Apple Inc", "sector": "Technology", "industry": "Consumer Electronics", "market_cap": 3_000_000_000_000, "exchange": "NASDAQ"},
    {"ticker": "GOOGL", "name": "Alphabet Inc", "sector": "Technology", "industry": "Software", "market_cap": 2_000_000_000_000, "exchange": "NASDAQ"},
    {"ticker": "META", "name": "Meta Platforms Inc", "sector": "Technology", "industry": "Software", "market_cap": 1_200_000_000_000, "exchange": "NASDAQ"},
    {"ticker": "AMZN", "name": "Amazon.com Inc", "sector": "Consumer Discretionary", "industry": "E-Commerce", "market_cap": 1_800_000_000_000, "exchange": "NASDAQ"},
    {"ticker": "NFLX", "name": "Netflix Inc", "sector": "Communication Services", "industry": "Entertainment", "market_cap": 250_000_000_000, "exchange": "NASDAQ"},
    {"ticker": "CRM", "name": "Salesforce Inc", "sector": "Technology", "industry": "Software", "market_cap": 300_000_000_000, "exchange": "NYSE"},
    {"ticker": "ADBE", "name": "Adobe Inc", "sector": "Technology", "industry": "Software", "market_cap": 250_000_000_000, "exchange": "NASDAQ"},

    # Additional companies for diversity
    {"ticker": "MO", "name": "Altria Group", "sector": "Consumer Staples", "industry": "Tobacco", "market_cap": 80_000_000_000, "exchange": "NYSE"},
    {"ticker": "PM", "name": "Philip Morris", "sector": "Consumer Staples", "industry": "Tobacco", "market_cap": 150_000_000_000, "exchange": "NYSE"},
    {"ticker": "WMT", "name": "Walmart Inc", "sector": "Consumer Staples", "industry": "Food Retail", "market_cap": 450_000_000_000, "exchange": "NYSE"},
    {"ticker": "COST", "name": "Costco Wholesale", "sector": "Consumer Staples", "industry": "Food Retail", "market_cap": 350_000_000_000, "exchange": "NASDAQ"},
    {"ticker": "LMT", "name": "Lockheed Martin", "sector": "Industrials", "industry": "Defense", "market_cap": 120_000_000_000, "exchange": "NYSE"},
    {"ticker": "RTX", "name": "RTX Corporation", "sector": "Industrials", "industry": "Defense", "market_cap": 150_000_000_000, "exchange": "NYSE"},
    {"ticker": "VZ", "name": "Verizon Communications", "sector": "Communication Services", "industry": "Telecom", "market_cap": 170_000_000_000, "exchange": "NYSE"},
    {"ticker": "T", "name": "AT&T Inc", "sector": "Communication Services", "industry": "Telecom", "market_cap": 130_000_000_000, "exchange": "NYSE"},
    {"ticker": "WM", "name": "Waste Management", "sector": "Industrials", "industry": "Waste Management", "market_cap": 85_000_000_000, "exchange": "NYSE"},
    {"ticker": "AWK", "name": "American Water Works", "sector": "Utilities", "industry": "Water Utilities", "market_cap": 28_000_000_000, "exchange": "NYSE"},
]


def generate_fundamentals(company: dict) -> dict:
    """Generate realistic fundamental data based on company characteristics."""
    industry = company.get("industry", "")
    market_cap = company.get("market_cap", 10_000_000_000)

    # Base multipliers
    assets_multiplier = random.uniform(0.8, 1.5)

    # Industry-specific adjustments
    if industry in ["Gold Mining", "Silver Mining", "Precious Metals"]:
        tangible_ratio = random.uniform(0.75, 0.90)
        foreign_revenue_pct = random.uniform(40, 70)
        pm_revenue_pct = random.uniform(80, 100)
        commodity_revenue_pct = random.uniform(85, 100)
        gross_margin = random.uniform(30, 50)
    elif industry in ["Precious Metals Royalties"]:
        tangible_ratio = random.uniform(0.20, 0.40)
        foreign_revenue_pct = random.uniform(50, 80)
        pm_revenue_pct = random.uniform(90, 100)
        commodity_revenue_pct = random.uniform(90, 100)
        gross_margin = random.uniform(70, 90)
    elif industry in ["Oil & Gas Integrated", "Oil & Gas E&P"]:
        tangible_ratio = random.uniform(0.70, 0.85)
        foreign_revenue_pct = random.uniform(30, 60)
        pm_revenue_pct = 0
        commodity_revenue_pct = random.uniform(75, 95)
        gross_margin = random.uniform(40, 60)
    elif industry in ["Copper Mining", "Diversified Mining"]:
        tangible_ratio = random.uniform(0.70, 0.85)
        foreign_revenue_pct = random.uniform(50, 80)
        pm_revenue_pct = random.uniform(0, 20)
        commodity_revenue_pct = random.uniform(85, 100)
        gross_margin = random.uniform(35, 55)
    elif industry in ["Banks", "Asset Management"]:
        tangible_ratio = random.uniform(0.05, 0.15)
        foreign_revenue_pct = random.uniform(15, 35)
        pm_revenue_pct = 0
        commodity_revenue_pct = 0
        gross_margin = random.uniform(50, 70)
    elif industry in ["Software"]:
        tangible_ratio = random.uniform(0.10, 0.25)
        foreign_revenue_pct = random.uniform(40, 60)
        pm_revenue_pct = 0
        commodity_revenue_pct = 0
        gross_margin = random.uniform(65, 85)
    elif industry in ["Electric Utilities", "Water Utilities", "Gas Utilities"]:
        tangible_ratio = random.uniform(0.75, 0.90)
        foreign_revenue_pct = random.uniform(0, 10)
        pm_revenue_pct = 0
        commodity_revenue_pct = random.uniform(0, 20)
        gross_margin = random.uniform(35, 50)
    else:
        tangible_ratio = random.uniform(0.40, 0.60)
        foreign_revenue_pct = random.uniform(20, 50)
        pm_revenue_pct = 0
        commodity_revenue_pct = random.uniform(0, 30)
        gross_margin = random.uniform(30, 50)

    total_assets = int(market_cap * assets_multiplier)
    tangible_assets = int(total_assets * tangible_ratio)
    total_revenue = int(market_cap * random.uniform(0.3, 0.8))
    total_debt = int(total_assets * random.uniform(0.20, 0.50))

    return {
        "fiscal_year": 2024,
        "fiscal_quarter": None,
        "report_type": "10-K",
        "total_assets": total_assets,
        "tangible_assets": tangible_assets,
        "intangible_assets": total_assets - tangible_assets,
        "total_revenue": total_revenue,
        "foreign_revenue_pct": Decimal(str(round(foreign_revenue_pct, 2))),
        "commodity_revenue_pct": Decimal(str(round(commodity_revenue_pct, 2))),
        "precious_metals_revenue_pct": Decimal(str(round(pm_revenue_pct, 2))),
        "gross_margin": Decimal(str(round(gross_margin, 2))),
        "gross_margin_5yr_std": Decimal(str(round(random.uniform(2, 10), 2))),
        "total_debt": total_debt,
        "fixed_rate_debt_pct": Decimal(str(round(random.uniform(50, 90), 2))),
        "avg_debt_maturity_years": Decimal(str(round(random.uniform(3, 12), 1))),
        "proven_reserves_oz": int(random.uniform(10_000_000, 150_000_000)) if "Mining" in industry else None,
    }


async def seed_database():
    """Main seed function."""
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if data already exists
        result = await session.execute(select(Company).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping...")
            return

        print("Seeding companies...")
        scoring_engine = ScoringEngine()
        today = date.today()

        for company_data in COMPANIES:
            # Create company
            company = Company(
                ticker=company_data["ticker"],
                name=company_data["name"],
                sector=company_data["sector"],
                industry=company_data["industry"],
                market_cap=company_data["market_cap"],
                exchange=company_data["exchange"],
                country="USA",
                is_active=True,
            )
            session.add(company)
            await session.flush()

            # Generate and add fundamentals
            fund_data = generate_fundamentals(company_data)
            fundamental = Fundamental(
                company_id=company.id,
                **fund_data
            )
            session.add(fundamental)

            # Calculate and add score
            company_scoring_data = CompanyData(
                ticker=company_data["ticker"],
                sector=company_data["sector"],
                industry=company_data["industry"],
                total_assets=fund_data["total_assets"],
                tangible_assets=fund_data["tangible_assets"],
                total_revenue=fund_data["total_revenue"],
                foreign_revenue_pct=fund_data["foreign_revenue_pct"],
                gross_margin=fund_data["gross_margin"],
                gross_margin_5yr_std=fund_data["gross_margin_5yr_std"],
                total_debt=fund_data["total_debt"],
                fixed_rate_debt_pct=fund_data["fixed_rate_debt_pct"],
                avg_debt_maturity_years=fund_data["avg_debt_maturity_years"],
                commodity_revenue_pct=fund_data["commodity_revenue_pct"],
                precious_metals_revenue_pct=fund_data["precious_metals_revenue_pct"],
                proven_reserves_oz=fund_data["proven_reserves_oz"],
            )

            result = scoring_engine.score(company_scoring_data)

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
                scoring_version=scoring_engine.VERSION,
            )
            session.add(score)

            print(f"  Added {company_data['ticker']}: {result.total_score} ({result.tier})")

        # Seed macro data for last 30 days
        print("\nSeeding macro data...")
        for i in range(30):
            data_date = today - timedelta(days=i)
            macro = MacroData(
                data_date=data_date,
                dxy_value=Decimal(str(round(100 + random.uniform(-5, 5), 2))),
                dxy_change_1d=Decimal(str(round(random.uniform(-0.5, 0.5), 4))),
                dxy_change_ytd=Decimal(str(round(random.uniform(-10, 5), 2))),
                gold_price=Decimal(str(round(2000 + random.uniform(-100, 200), 2))),
                silver_price=Decimal(str(round(25 + random.uniform(-2, 5), 2))),
                oil_wti_price=Decimal(str(round(75 + random.uniform(-10, 15), 2))),
                m2_supply_trillions=Decimal(str(round(21 + random.uniform(-0.5, 0.5), 3))),
                m2_yoy_change=Decimal(str(round(random.uniform(-2, 8), 2))),
                fed_funds_rate=Decimal("5.25"),
                ten_year_yield=Decimal(str(round(4 + random.uniform(-0.5, 0.5), 2))),
                cpi_yoy=Decimal(str(round(3 + random.uniform(-0.5, 1), 2))),
            )
            session.add(macro)

        await session.commit()
        print(f"\nSeeded {len(COMPANIES)} companies and 30 days of macro data.")


if __name__ == "__main__":
    asyncio.run(seed_database())
