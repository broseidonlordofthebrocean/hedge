import pytest
from decimal import Decimal

from app.services.scoring.factors import CompanyData


@pytest.fixture
def gold_miner():
    """Sample gold mining company data."""
    return CompanyData(
        ticker="NEM",
        sector="Materials",
        industry="Gold Mining",
        total_assets=35_000_000_000,
        tangible_assets=30_000_000_000,
        total_revenue=12_000_000_000,
        foreign_revenue_pct=Decimal("45"),
        gross_margin=Decimal("35"),
        gross_margin_5yr_std=Decimal("5"),
        total_debt=8_000_000_000,
        fixed_rate_debt_pct=Decimal("75"),
        avg_debt_maturity_years=Decimal("8"),
        proven_reserves_oz=100_000_000,
    )


@pytest.fixture
def bank():
    """Sample bank company data."""
    return CompanyData(
        ticker="JPM",
        sector="Financials",
        industry="Banks",
        total_assets=3_000_000_000_000,
        tangible_assets=300_000_000_000,
        total_revenue=150_000_000_000,
        foreign_revenue_pct=Decimal("25"),
        gross_margin=Decimal("60"),
        gross_margin_5yr_std=Decimal("8"),
        total_debt=500_000_000_000,
        fixed_rate_debt_pct=Decimal("40"),
        avg_debt_maturity_years=Decimal("3"),
    )


@pytest.fixture
def utility():
    """Sample utility company data."""
    return CompanyData(
        ticker="NEE",
        sector="Utilities",
        industry="Electric Utilities",
        total_assets=150_000_000_000,
        tangible_assets=120_000_000_000,
        total_revenue=25_000_000_000,
        foreign_revenue_pct=Decimal("5"),
        gross_margin=Decimal("45"),
        gross_margin_5yr_std=Decimal("3"),
        total_debt=70_000_000_000,
        fixed_rate_debt_pct=Decimal("90"),
        avg_debt_maturity_years=Decimal("15"),
    )
