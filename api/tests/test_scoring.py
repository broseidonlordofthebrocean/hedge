import pytest
from decimal import Decimal

from app.services.scoring import ScoringEngine, FactorScorer
from app.services.scoring.factors import CompanyData
from app.services.scoring.weights import get_tier


class TestFactorScorer:
    """Tests for individual factor scoring."""

    def test_hard_assets_high_tangible(self, gold_miner):
        """Companies with high tangible assets should score well."""
        scorer = FactorScorer()
        score = scorer.score_hard_assets(gold_miner)
        assert score >= Decimal("60")

    def test_hard_assets_low_tangible(self, bank):
        """Banks with low tangible ratio should score poorly."""
        scorer = FactorScorer()
        score = scorer.score_hard_assets(bank)
        assert score < Decimal("30")

    def test_precious_metals_miner(self, gold_miner):
        """Gold miners should get high precious metals score."""
        scorer = FactorScorer()
        score = scorer.score_precious_metals(gold_miner)
        assert score >= Decimal("80")

    def test_precious_metals_bank(self, bank):
        """Banks should get low precious metals score."""
        scorer = FactorScorer()
        score = scorer.score_precious_metals(bank)
        assert score <= Decimal("10")

    def test_essential_services_utility(self, utility):
        """Utilities should score high on essential services."""
        scorer = FactorScorer()
        score = scorer.score_essential_services(utility)
        assert score >= Decimal("90")

    def test_essential_services_bank(self, bank):
        """Banks should score low on essential services."""
        scorer = FactorScorer()
        score = scorer.score_essential_services(bank)
        assert score <= Decimal("40")

    def test_foreign_revenue_high_exposure(self):
        """Companies with high foreign revenue should score well."""
        scorer = FactorScorer()
        data = CompanyData(ticker="TEST", foreign_revenue_pct=Decimal("70"))
        score = scorer.score_foreign_revenue(data)
        assert score >= Decimal("90")

    def test_foreign_revenue_domestic(self):
        """Domestic-focused companies should score lower."""
        scorer = FactorScorer()
        data = CompanyData(ticker="TEST", foreign_revenue_pct=Decimal("10"))
        score = scorer.score_foreign_revenue(data)
        assert score <= Decimal("20")


class TestScoringEngine:
    """Tests for the main scoring engine."""

    def test_gold_miner_scores_high(self, gold_miner):
        """Gold miners should get high overall scores."""
        engine = ScoringEngine()
        result = engine.score(gold_miner)

        assert result.total_score >= Decimal("70")
        assert result.tier in ["excellent", "strong"]

    def test_bank_scores_low(self, bank):
        """Banks should get lower overall scores."""
        engine = ScoringEngine()
        result = engine.score(bank)

        assert result.total_score < Decimal("55")
        assert result.tier in ["vulnerable", "critical", "moderate"]

    def test_scenario_scores_calculated(self, gold_miner):
        """All scenario scores should be calculated."""
        engine = ScoringEngine()
        result = engine.score(gold_miner)

        assert "current" in result.scenario_scores
        assert "gradual" in result.scenario_scores
        assert "rapid" in result.scenario_scores
        assert "hyper" in result.scenario_scores

    def test_hyper_scenario_weights_pm_higher(self, gold_miner):
        """In hyper scenario, PM exposure matters more."""
        engine = ScoringEngine()
        result = engine.score(gold_miner)

        # Gold miner should do better in hyper scenario
        assert result.scenario_scores["hyper"] >= result.scenario_scores["current"]

    def test_confidence_increases_with_data(self):
        """Confidence should increase with more data."""
        engine = ScoringEngine()

        sparse_data = CompanyData(ticker="TEST")
        full_data = CompanyData(
            ticker="TEST",
            total_assets=1000000,
            tangible_assets=800000,
            total_revenue=500000,
            foreign_revenue_pct=Decimal("30"),
            gross_margin=Decimal("40"),
            gross_margin_5yr_std=Decimal("5"),
            total_debt=200000,
            fixed_rate_debt_pct=Decimal("60"),
            avg_debt_maturity_years=Decimal("5"),
            commodity_revenue_pct=Decimal("10"),
        )

        sparse_result = engine.score(sparse_data)
        full_result = engine.score(full_data)

        assert full_result.confidence > sparse_result.confidence


class TestTierClassification:
    """Tests for tier classification."""

    def test_excellent_tier(self):
        assert get_tier(Decimal("90")) == "excellent"
        assert get_tier(Decimal("85")) == "excellent"

    def test_strong_tier(self):
        assert get_tier(Decimal("75")) == "strong"
        assert get_tier(Decimal("70")) == "strong"

    def test_moderate_tier(self):
        assert get_tier(Decimal("60")) == "moderate"
        assert get_tier(Decimal("55")) == "moderate"

    def test_vulnerable_tier(self):
        assert get_tier(Decimal("50")) == "vulnerable"
        assert get_tier(Decimal("40")) == "vulnerable"

    def test_critical_tier(self):
        assert get_tier(Decimal("30")) == "critical"
        assert get_tier(Decimal("0")) == "critical"


class TestPortfolioScoring:
    """Tests for portfolio-level scoring."""

    def test_portfolio_weighted_score(self, gold_miner, bank):
        """Portfolio score should be value-weighted."""
        engine = ScoringEngine()

        holdings = [
            (gold_miner, Decimal("10000")),
            (bank, Decimal("10000")),
        ]

        result = engine.score_portfolio(holdings)

        assert result["overall_score"] is not None
        assert result["total_value"] == 20000.0
        assert len(result["holdings_analysis"]) == 2

    def test_empty_portfolio(self):
        """Empty portfolio should return None scores."""
        engine = ScoringEngine()
        result = engine.score_portfolio([])

        assert result["overall_score"] is None

    def test_recommendations_generated(self, gold_miner, bank):
        """Recommendations should be generated for low-scoring holdings."""
        engine = ScoringEngine()

        holdings = [
            (gold_miner, Decimal("5000")),
            (bank, Decimal("15000")),  # Heavy bank weight
        ]

        portfolio_result = engine.score_portfolio(holdings)
        recommendations = engine.generate_recommendations(
            portfolio_result["holdings_analysis"]
        )

        # Should recommend reducing bank position
        reduce_recs = [r for r in recommendations if r["action"] == "reduce"]
        assert len(reduce_recs) > 0
