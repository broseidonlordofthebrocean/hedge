from dataclasses import dataclass
from decimal import Decimal


@dataclass
class FactorWeights:
    """Configuration for factor weights in scoring calculation."""
    hard_assets: Decimal = Decimal("0.25")
    precious_metals: Decimal = Decimal("0.15")
    commodities: Decimal = Decimal("0.15")
    foreign_revenue: Decimal = Decimal("0.15")
    pricing_power: Decimal = Decimal("0.15")
    debt_structure: Decimal = Decimal("0.10")
    essential_services: Decimal = Decimal("0.05")

    def validate(self) -> bool:
        """Ensure weights sum to 1.0"""
        total = (
            self.hard_assets +
            self.precious_metals +
            self.commodities +
            self.foreign_revenue +
            self.pricing_power +
            self.debt_structure +
            self.essential_services
        )
        return abs(total - Decimal("1.0")) < Decimal("0.001")

    def to_dict(self) -> dict[str, Decimal]:
        return {
            "hard_assets": self.hard_assets,
            "precious_metals": self.precious_metals,
            "commodities": self.commodities,
            "foreign_revenue": self.foreign_revenue,
            "pricing_power": self.pricing_power,
            "debt_structure": self.debt_structure,
            "essential_services": self.essential_services,
        }


# Default weights for current scenario
DEFAULT_WEIGHTS = FactorWeights()

# Scenario-specific weights
GRADUAL_WEIGHTS = FactorWeights(
    hard_assets=Decimal("0.25"),
    precious_metals=Decimal("0.15"),
    commodities=Decimal("0.15"),
    foreign_revenue=Decimal("0.15"),
    pricing_power=Decimal("0.15"),
    debt_structure=Decimal("0.10"),
    essential_services=Decimal("0.05"),
)

RAPID_WEIGHTS = FactorWeights(
    hard_assets=Decimal("0.30"),
    precious_metals=Decimal("0.25"),
    commodities=Decimal("0.20"),
    foreign_revenue=Decimal("0.10"),
    pricing_power=Decimal("0.10"),
    debt_structure=Decimal("0.05"),
    essential_services=Decimal("0.00"),
)

HYPER_WEIGHTS = FactorWeights(
    hard_assets=Decimal("0.35"),
    precious_metals=Decimal("0.35"),
    commodities=Decimal("0.20"),
    foreign_revenue=Decimal("0.05"),
    pricing_power=Decimal("0.05"),
    debt_structure=Decimal("0.00"),
    essential_services=Decimal("0.00"),
)

SCENARIO_WEIGHTS = {
    "current": DEFAULT_WEIGHTS,
    "gradual": GRADUAL_WEIGHTS,
    "rapid": RAPID_WEIGHTS,
    "hyper": HYPER_WEIGHTS,
}


# Tier thresholds
TIER_THRESHOLDS = {
    "excellent": (Decimal("85"), Decimal("100")),
    "strong": (Decimal("70"), Decimal("84.99")),
    "moderate": (Decimal("55"), Decimal("69.99")),
    "vulnerable": (Decimal("40"), Decimal("54.99")),
    "critical": (Decimal("0"), Decimal("39.99")),
}


def get_tier(score: Decimal) -> str:
    """Determine tier classification based on score."""
    for tier, (min_score, max_score) in TIER_THRESHOLDS.items():
        if min_score <= score <= max_score:
            return tier
    return "critical"
