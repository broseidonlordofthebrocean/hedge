from decimal import Decimal
from dataclasses import dataclass
from typing import Optional

from .factors import FactorScorer, CompanyData
from .scenarios import ScenarioModeler
from .weights import DEFAULT_WEIGHTS, get_tier, FactorWeights


@dataclass
class ScoringResult:
    """Complete scoring result for a company."""
    total_score: Decimal
    tier: str
    confidence: Decimal
    factors: dict[str, Decimal]
    scenario_scores: dict[str, Decimal]


class ScoringEngine:
    """
    Main scoring engine that orchestrates factor scoring and scenario modeling.
    This is the heart of the HEDGE platform.
    """

    VERSION = "1.0.0"

    def __init__(self, weights: Optional[FactorWeights] = None):
        self.weights = weights or DEFAULT_WEIGHTS
        self.factor_scorer = FactorScorer()
        self.scenario_modeler = ScenarioModeler()

    def score(self, data: CompanyData) -> ScoringResult:
        """
        Calculate complete survival score for a company.

        Args:
            data: CompanyData with all relevant fundamentals

        Returns:
            ScoringResult with total score, tier, factors, and scenarios
        """
        # Calculate individual factor scores
        factor_scores = self.factor_scorer.score_all(data)

        # Calculate weighted total score
        total_score = self._calculate_weighted_score(factor_scores)

        # Determine tier
        tier = get_tier(total_score)

        # Calculate confidence based on data completeness
        confidence = self._calculate_confidence(data)

        # Calculate scenario-specific scores
        scenario_scores = self.scenario_modeler.calculate_all_scenarios(factor_scores)

        return ScoringResult(
            total_score=total_score,
            tier=tier,
            confidence=confidence,
            factors=factor_scores,
            scenario_scores=scenario_scores,
        )

    def _calculate_weighted_score(self, factor_scores: dict[str, Decimal]) -> Decimal:
        """Calculate weighted average of factor scores."""
        total = Decimal("0")
        weights_dict = self.weights.to_dict()

        for factor, score in factor_scores.items():
            weight = weights_dict.get(factor, Decimal("0"))
            total += score * weight

        return round(total, 2)

    def _calculate_confidence(self, data: CompanyData) -> Decimal:
        """
        Calculate confidence score based on data completeness.
        More complete data = higher confidence in the score.
        """
        data_points = [
            data.total_assets is not None,
            data.tangible_assets is not None,
            data.total_revenue is not None,
            data.foreign_revenue_pct is not None,
            data.gross_margin is not None,
            data.gross_margin_5yr_std is not None,
            data.total_debt is not None,
            data.fixed_rate_debt_pct is not None,
            data.avg_debt_maturity_years is not None,
            data.commodity_revenue_pct is not None,
        ]

        available = sum(data_points)
        total = len(data_points)

        # Base confidence of 0.3, up to 1.0 with full data
        confidence = Decimal("0.3") + (Decimal(str(available)) / Decimal(str(total))) * Decimal("0.7")

        return round(confidence, 2)

    def score_portfolio(
        self,
        holdings: list[tuple[CompanyData, Decimal]]
    ) -> dict:
        """
        Score an entire portfolio.

        Args:
            holdings: List of (CompanyData, value) tuples

        Returns:
            Portfolio-level analysis including weighted scores and recommendations
        """
        if not holdings:
            return {
                "overall_score": None,
                "weighted_by_value": None,
                "holdings_analysis": [],
            }

        total_value = sum(value for _, value in holdings)
        weighted_score = Decimal("0")
        holdings_analysis = []

        for company_data, value in holdings:
            result = self.score(company_data)
            weight = value / total_value if total_value > 0 else Decimal("0")
            weighted_score += result.total_score * weight

            holdings_analysis.append({
                "ticker": company_data.ticker,
                "value": float(value),
                "weight": float(round(weight * 100, 2)),
                "score": float(result.total_score),
                "tier": result.tier,
                "factors": {k: float(v) for k, v in result.factors.items()},
            })

        # Calculate portfolio-level scenario scores
        scenario_weighted_scores = {
            "gradual": Decimal("0"),
            "rapid": Decimal("0"),
            "hyper": Decimal("0"),
        }

        for company_data, value in holdings:
            result = self.score(company_data)
            weight = value / total_value if total_value > 0 else Decimal("0")
            for scenario in scenario_weighted_scores:
                scenario_weighted_scores[scenario] += result.scenario_scores[scenario] * weight

        return {
            "overall_score": float(round(weighted_score, 2)),
            "weighted_by_value": float(round(weighted_score, 2)),
            "scenario_scores": {k: float(round(v, 2)) for k, v in scenario_weighted_scores.items()},
            "tier": get_tier(weighted_score),
            "holdings_analysis": sorted(holdings_analysis, key=lambda x: x["score"], reverse=True),
            "total_value": float(total_value),
        }

    def generate_recommendations(
        self,
        holdings_analysis: list[dict],
        target_score: Decimal = Decimal("70")
    ) -> list[dict]:
        """
        Generate recommendations to improve portfolio score.
        """
        recommendations = []

        # Find holdings that drag down the score
        for holding in holdings_analysis:
            if Decimal(str(holding["score"])) < Decimal("50"):
                recommendations.append({
                    "action": "reduce",
                    "ticker": holding["ticker"],
                    "reason": f"Low survival score ({holding['score']}) in devaluation scenarios",
                    "current_weight": holding["weight"],
                })

        # Suggest adding high-scoring assets if portfolio score is low
        avg_score = sum(h["score"] for h in holdings_analysis) / len(holdings_analysis) if holdings_analysis else 0
        if Decimal(str(avg_score)) < target_score:
            recommendations.append({
                "action": "add",
                "suggestion": "precious_metals",
                "reason": "Increase precious metals exposure for better devaluation hedge",
            })
            recommendations.append({
                "action": "add",
                "suggestion": "commodities",
                "reason": "Add commodity producers for hard asset exposure",
            })

        return recommendations
