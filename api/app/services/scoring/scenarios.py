from decimal import Decimal
from .weights import FactorWeights, SCENARIO_WEIGHTS


class ScenarioModeler:
    """Model different dollar devaluation scenarios and their impact on scores."""

    SCENARIOS = {
        "gradual": {
            "name": "Gradual Decline",
            "description": "15-20% decline over 3-5 years",
            "dollar_decline_pct": 17.5,
            "timeline_months": 48,
            "inflation_rate": 6,
        },
        "rapid": {
            "name": "Rapid Decline",
            "description": "30-40% decline in 12-18 months",
            "dollar_decline_pct": 35,
            "timeline_months": 15,
            "inflation_rate": 12,
        },
        "hyper": {
            "name": "Hyperinflation",
            "description": "50%+ collapse, hyperinflation event",
            "dollar_decline_pct": 55,
            "timeline_months": 6,
            "inflation_rate": 50,
        },
    }

    def get_scenario_weights(self, scenario: str) -> FactorWeights:
        """Get factor weights adjusted for specific scenario."""
        return SCENARIO_WEIGHTS.get(scenario, SCENARIO_WEIGHTS["current"])

    def calculate_scenario_score(
        self,
        factor_scores: dict[str, Decimal],
        scenario: str
    ) -> Decimal:
        """
        Calculate weighted score for a specific scenario.
        More severe scenarios weight hard assets and PM higher.
        """
        weights = self.get_scenario_weights(scenario)

        total = Decimal("0")
        for factor, score in factor_scores.items():
            weight = getattr(weights, factor, Decimal("0"))
            total += score * weight

        return round(total, 2)

    def calculate_all_scenarios(
        self,
        factor_scores: dict[str, Decimal]
    ) -> dict[str, Decimal]:
        """Calculate scores for all scenarios."""
        return {
            "current": self.calculate_scenario_score(factor_scores, "current"),
            "gradual": self.calculate_scenario_score(factor_scores, "gradual"),
            "rapid": self.calculate_scenario_score(factor_scores, "rapid"),
            "hyper": self.calculate_scenario_score(factor_scores, "hyper"),
        }

    def model_portfolio_impact(
        self,
        portfolio_value: Decimal,
        survival_score: Decimal,
        scenario: str
    ) -> dict:
        """
        Model the impact of a scenario on a portfolio's value.
        Returns projected nominal and real values.
        """
        if scenario not in self.SCENARIOS:
            scenario = "gradual"

        params = self.SCENARIOS[scenario]
        dollar_decline = Decimal(str(params["dollar_decline_pct"])) / Decimal("100")
        inflation = Decimal(str(params["inflation_rate"])) / Decimal("100")
        timeline_years = Decimal(str(params["timeline_months"])) / Decimal("12")

        # Higher survival score = better performance in devaluation
        # Score 100 = fully hedged, maintains real value
        # Score 0 = fully exposed, loses in line with dollar
        hedge_ratio = survival_score / Decimal("100")

        # Calculate projected nominal value
        # Well-hedged assets should appreciate nominally as dollar declines
        nominal_change = dollar_decline * hedge_ratio - dollar_decline * (1 - hedge_ratio) * Decimal("0.5")
        projected_nominal = portfolio_value * (1 + nominal_change)

        # Calculate projected real value (purchasing power)
        cumulative_inflation = (1 + inflation) ** float(timeline_years) - 1
        projected_real = projected_nominal / (1 + Decimal(str(cumulative_inflation)))

        return {
            "current_value": float(portfolio_value),
            "projected_nominal": float(round(projected_nominal, 2)),
            "projected_real": float(round(projected_real, 2)),
            "nominal_change_pct": float(round(nominal_change * 100, 2)),
            "real_change_pct": float(round((projected_real / portfolio_value - 1) * 100, 2)),
            "scenario_params": params,
        }

    def get_scenario_info(self, scenario: str) -> dict:
        """Get information about a specific scenario."""
        return self.SCENARIOS.get(scenario, self.SCENARIOS["gradual"])
