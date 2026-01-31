from decimal import Decimal
from typing import Optional
from dataclasses import dataclass


@dataclass
class CompanyData:
    """Data needed for scoring a company."""
    ticker: str
    sector: Optional[str] = None
    industry: Optional[str] = None

    # Balance sheet
    total_assets: Optional[int] = None
    tangible_assets: Optional[int] = None
    intangible_assets: Optional[int] = None

    # Revenue breakdown
    total_revenue: Optional[int] = None
    foreign_revenue: Optional[int] = None
    foreign_revenue_pct: Optional[Decimal] = None
    commodity_revenue: Optional[int] = None
    commodity_revenue_pct: Optional[Decimal] = None
    precious_metals_revenue: Optional[int] = None
    precious_metals_revenue_pct: Optional[Decimal] = None

    # Debt structure
    total_debt: Optional[int] = None
    fixed_rate_debt_pct: Optional[Decimal] = None
    avg_debt_maturity_years: Optional[Decimal] = None

    # Profitability
    gross_margin: Optional[Decimal] = None
    gross_margin_5yr_std: Optional[Decimal] = None

    # Mining specific
    proven_reserves_oz: Optional[int] = None


# Industry-specific base scores for essential services
ESSENTIAL_SCORES = {
    "Electric Utilities": 95,
    "Water Utilities": 95,
    "Gas Utilities": 90,
    "Healthcare Facilities": 90,
    "Pharmaceuticals": 85,
    "Food Products": 85,
    "Food Retail": 80,
    "Household Products": 75,
    "Waste Management": 75,
    "Telecom": 70,
    "Defense": 70,
    "Insurance": 40,
    "Banks": 35,
    "Asset Management": 30,
    "Software": 25,
    "Consumer Discretionary": 20,
}

# Commodity sector base scores
COMMODITY_SECTOR_SCORES = {
    "Oil & Gas E&P": 85,
    "Oil & Gas Integrated": 80,
    "Copper Mining": 85,
    "Diversified Mining": 75,
    "Agricultural Products": 70,
    "Steel": 65,
    "Chemicals": 55,
}

# Precious metals industries
PRECIOUS_METALS_INDUSTRIES = ["Gold Mining", "Silver Mining", "Precious Metals", "Precious Metals Royalties"]


class FactorScorer:
    """Calculate individual factor scores for a company."""

    @staticmethod
    def score_hard_assets(data: CompanyData) -> Decimal:
        """
        Calculate hard asset score based on tangible/total asset ratio.
        Returns a score from 0-100 where higher indicates more hard asset backing.
        """
        if not data.total_assets or data.total_assets == 0:
            return Decimal("50")  # Neutral if unknown

        tangible = data.tangible_assets or 0
        tangible_ratio = Decimal(tangible) / Decimal(data.total_assets)

        # Base score from tangible ratio (0-80 points)
        base_score = tangible_ratio * Decimal("80")

        # Boost for specific hard asset types
        real_estate_boost = Decimal("10") if data.industry in ["REITs", "Real Estate"] else Decimal("0")
        mining_boost = Decimal("10") if data.industry and "Mining" in data.industry else Decimal("0")

        total = base_score + real_estate_boost + mining_boost
        return min(total, Decimal("100"))

    @staticmethod
    def score_precious_metals(data: CompanyData) -> Decimal:
        """
        Calculate precious metals exposure score.
        Direct miners get top scores.
        """
        # Direct miners get top scores
        if data.industry in PRECIOUS_METALS_INDUSTRIES:
            base = Decimal("80")
            # Boost for reserves
            if data.proven_reserves_oz:
                reserve_factor = min(Decimal(data.proven_reserves_oz) / Decimal("10000000"), Decimal("1")) * Decimal("20")
                return min(base + reserve_factor, Decimal("100"))
            return base

        # Royalty/streaming companies
        if data.industry == "Precious Metals Royalties":
            return Decimal("85")

        # Other companies: based on PM revenue exposure
        pm_pct = data.precious_metals_revenue_pct or Decimal("0")
        return min(pm_pct * Decimal("2"), Decimal("100"))

    @staticmethod
    def score_commodities(data: CompanyData) -> Decimal:
        """
        Calculate commodity exposure score.
        Based on sector and actual commodity revenue.
        """
        sector_base = Decimal(str(COMMODITY_SECTOR_SCORES.get(data.industry or "", 30)))

        # Adjust based on actual commodity revenue
        commodity_pct = data.commodity_revenue_pct or Decimal("0")
        revenue_adjustment = (commodity_pct - Decimal("50")) * Decimal("0.3")  # +/- 15 points

        return max(Decimal("0"), min(sector_base + revenue_adjustment, Decimal("100")))

    @staticmethod
    def score_foreign_revenue(data: CompanyData) -> Decimal:
        """
        Calculate foreign revenue score.
        Higher international exposure = better hedge against USD.
        """
        foreign_pct = data.foreign_revenue_pct or Decimal("0")

        # Linear scale with boost for very high international
        if foreign_pct >= Decimal("70"):
            return Decimal("95")
        elif foreign_pct >= Decimal("50"):
            return Decimal("70") + (foreign_pct - Decimal("50")) * Decimal("1.25")
        else:
            return foreign_pct * Decimal("1.4")

    @staticmethod
    def score_pricing_power(data: CompanyData) -> Decimal:
        """
        Calculate pricing power score based on margin and stability.
        High margin + low variance = strong pricing power.
        """
        margin = data.gross_margin or Decimal("0")
        stability = data.gross_margin_5yr_std or Decimal("10")  # Default to moderate variance

        # High margin = can absorb cost increases (0-50 points)
        margin_score = min(margin * Decimal("1.2"), Decimal("50"))

        # Low variance = consistent pricing power (0-50 points)
        stability_score = max(Decimal("50") - (stability * Decimal("5")), Decimal("0"))

        return margin_score + stability_score

    @staticmethod
    def score_debt_structure(data: CompanyData) -> Decimal:
        """
        Calculate debt structure score.
        Fixed rate, long maturity, low leverage = good.
        """
        # Fixed rate debt is good (inflates away) - 0-50 points
        fixed_pct = data.fixed_rate_debt_pct or Decimal("50")
        fixed_score = fixed_pct * Decimal("0.5")

        # Longer maturity is good - 0-30 points
        maturity = data.avg_debt_maturity_years or Decimal("5")
        maturity_score = min(maturity * Decimal("5"), Decimal("30"))

        # Low debt/assets ratio is good - 0-20 points
        if data.total_assets and data.total_debt:
            debt_ratio = Decimal(data.total_debt) / Decimal(data.total_assets)
            leverage_score = max(Decimal("20") - (debt_ratio * Decimal("40")), Decimal("0"))
        else:
            leverage_score = Decimal("10")

        return fixed_score + maturity_score + leverage_score

    @staticmethod
    def score_essential_services(data: CompanyData) -> Decimal:
        """
        Calculate essential services score based on industry.
        Essential/defensive sectors score higher.
        """
        return Decimal(str(ESSENTIAL_SCORES.get(data.industry or "", 40)))

    def score_all(self, data: CompanyData) -> dict[str, Decimal]:
        """Calculate all factor scores for a company."""
        return {
            "hard_assets": self.score_hard_assets(data),
            "precious_metals": self.score_precious_metals(data),
            "commodities": self.score_commodities(data),
            "foreign_revenue": self.score_foreign_revenue(data),
            "pricing_power": self.score_pricing_power(data),
            "debt_structure": self.score_debt_structure(data),
            "essential_services": self.score_essential_services(data),
        }
