"""Portfolio API v1 endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...database import get_db
from ...deps import require_user
from ...models import Portfolio, PortfolioHolding, Company, SurvivalScore, UserProfile

router = APIRouter()


class PortfolioCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class HoldingCreate(BaseModel):
    ticker: str
    shares: Decimal
    cost_basis: Optional[Decimal] = None


class HoldingUpdate(BaseModel):
    shares: Optional[Decimal] = None
    cost_basis: Optional[Decimal] = None


class ScenarioRequest(BaseModel):
    scenario: str
    custom_params: Optional[dict] = None


@router.get("")
async def list_portfolios(
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's portfolios."""
    query = (
        select(Portfolio)
        .where(Portfolio.user_id == user.id)
        .options(selectinload(Portfolio.holdings))
        .order_by(Portfolio.is_primary.desc(), Portfolio.name)
    )

    result = await db.execute(query)
    portfolios = result.scalars().all()

    return {
        "data": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "is_primary": p.is_primary,
                "holdings_count": len(p.holdings),
                "total_value": float(p.total_value) if p.total_value else None,
                "survival_score": float(p.survival_score) if p.survival_score else None,
                "created_at": p.created_at,
            }
            for p in portfolios
        ]
    }


@router.post("")
async def create_portfolio(
    portfolio: PortfolioCreate,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new portfolio."""
    # Check portfolio limit based on tier
    count_query = select(func.count(Portfolio.id)).where(Portfolio.user_id == user.id)
    count_result = await db.execute(count_query)
    current_count = count_result.scalar() or 0

    max_portfolios = {"free": 1, "pro": 3, "institutional": 100}.get(
        user.subscription_tier, 1
    )

    if current_count >= max_portfolios:
        raise HTTPException(
            status_code=403,
            detail=f"Portfolio limit reached ({max_portfolios}). Upgrade to create more.",
        )

    new_portfolio = Portfolio(
        user_id=user.id,
        name=portfolio.name,
        description=portfolio.description,
        is_primary=current_count == 0,  # First portfolio is primary
    )
    db.add(new_portfolio)
    await db.commit()
    await db.refresh(new_portfolio)

    return {
        "id": str(new_portfolio.id),
        "name": new_portfolio.name,
        "description": new_portfolio.description,
        "is_primary": new_portfolio.is_primary,
        "created_at": new_portfolio.created_at,
    }


@router.get("/{portfolio_id}")
async def get_portfolio(
    portfolio_id: str,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Get portfolio with holdings."""
    query = (
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
        .options(selectinload(Portfolio.holdings).selectinload(PortfolioHolding.company))
    )

    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Get latest scores for holdings
    holdings_data = []
    for holding in portfolio.holdings:
        # Get latest score
        score_query = (
            select(SurvivalScore)
            .where(SurvivalScore.company_id == holding.company_id)
            .order_by(SurvivalScore.score_date.desc())
            .limit(1)
        )
        score_result = await db.execute(score_query)
        score = score_result.scalar_one_or_none()

        holdings_data.append({
            "id": str(holding.id),
            "ticker": holding.company.ticker if holding.company else None,
            "name": holding.company.name if holding.company else None,
            "shares": float(holding.shares),
            "cost_basis": float(holding.cost_basis) if holding.cost_basis else None,
            "current_price": float(holding.current_price) if holding.current_price else None,
            "current_value": float(holding.current_value) if holding.current_value else None,
            "gain_loss": float(holding.gain_loss) if holding.gain_loss else None,
            "gain_loss_pct": float(holding.gain_loss_pct) if holding.gain_loss_pct else None,
            "score": float(score.total_score) if score else None,
            "tier": score.tier if score else None,
        })

    return {
        "id": str(portfolio.id),
        "name": portfolio.name,
        "description": portfolio.description,
        "is_primary": portfolio.is_primary,
        "total_value": float(portfolio.total_value) if portfolio.total_value else None,
        "survival_score": float(portfolio.survival_score) if portfolio.survival_score else None,
        "scenario_scores": {
            "gradual": float(portfolio.scenario_gradual_score) if portfolio.scenario_gradual_score else None,
            "rapid": float(portfolio.scenario_rapid_score) if portfolio.scenario_rapid_score else None,
            "hyper": float(portfolio.scenario_hyper_score) if portfolio.scenario_hyper_score else None,
        },
        "holdings": holdings_data,
        "created_at": portfolio.created_at,
        "updated_at": portfolio.updated_at,
    }


@router.put("/{portfolio_id}")
async def update_portfolio(
    portfolio_id: str,
    portfolio_update: PortfolioUpdate,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Update portfolio details."""
    query = select(Portfolio).where(
        Portfolio.id == portfolio_id, Portfolio.user_id == user.id
    )
    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    if portfolio_update.name is not None:
        portfolio.name = portfolio_update.name
    if portfolio_update.description is not None:
        portfolio.description = portfolio_update.description

    await db.commit()
    await db.refresh(portfolio)

    return {
        "id": str(portfolio.id),
        "name": portfolio.name,
        "description": portfolio.description,
        "updated_at": portfolio.updated_at,
    }


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a portfolio."""
    query = select(Portfolio).where(
        Portfolio.id == portfolio_id, Portfolio.user_id == user.id
    )
    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    await db.delete(portfolio)
    await db.commit()

    return {"success": True}


@router.post("/{portfolio_id}/holdings")
async def add_holding(
    portfolio_id: str,
    holding: HoldingCreate,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a holding to a portfolio."""
    # Verify portfolio ownership
    portfolio_query = select(Portfolio).where(
        Portfolio.id == portfolio_id, Portfolio.user_id == user.id
    )
    portfolio_result = await db.execute(portfolio_query)
    portfolio = portfolio_result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Find company
    company_query = select(Company).where(Company.ticker == holding.ticker.upper())
    company_result = await db.execute(company_query)
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company {holding.ticker} not found")

    # Check if holding already exists
    existing_query = select(PortfolioHolding).where(
        PortfolioHolding.portfolio_id == portfolio_id,
        PortfolioHolding.company_id == company.id,
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalar_one_or_none()

    if existing:
        # Update existing holding
        existing.shares = holding.shares
        if holding.cost_basis is not None:
            existing.cost_basis = holding.cost_basis
        await db.commit()
        await db.refresh(existing)
        return {
            "id": str(existing.id),
            "ticker": company.ticker,
            "shares": float(existing.shares),
            "cost_basis": float(existing.cost_basis) if existing.cost_basis else None,
        }

    # Create new holding
    new_holding = PortfolioHolding(
        portfolio_id=portfolio_id,
        company_id=company.id,
        shares=holding.shares,
        cost_basis=holding.cost_basis,
    )
    db.add(new_holding)
    await db.commit()
    await db.refresh(new_holding)

    return {
        "id": str(new_holding.id),
        "ticker": company.ticker,
        "shares": float(new_holding.shares),
        "cost_basis": float(new_holding.cost_basis) if new_holding.cost_basis else None,
    }


@router.put("/{portfolio_id}/holdings/{holding_id}")
async def update_holding(
    portfolio_id: str,
    holding_id: str,
    holding_update: HoldingUpdate,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a portfolio holding."""
    # Verify ownership through portfolio
    query = (
        select(PortfolioHolding)
        .join(Portfolio)
        .where(
            PortfolioHolding.id == holding_id,
            PortfolioHolding.portfolio_id == portfolio_id,
            Portfolio.user_id == user.id,
        )
    )
    result = await db.execute(query)
    holding = result.scalar_one_or_none()

    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    if holding_update.shares is not None:
        holding.shares = holding_update.shares
    if holding_update.cost_basis is not None:
        holding.cost_basis = holding_update.cost_basis

    await db.commit()
    await db.refresh(holding)

    return {
        "id": str(holding.id),
        "shares": float(holding.shares),
        "cost_basis": float(holding.cost_basis) if holding.cost_basis else None,
    }


@router.delete("/{portfolio_id}/holdings/{holding_id}")
async def delete_holding(
    portfolio_id: str,
    holding_id: str,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a holding from a portfolio."""
    query = (
        select(PortfolioHolding)
        .join(Portfolio)
        .where(
            PortfolioHolding.id == holding_id,
            PortfolioHolding.portfolio_id == portfolio_id,
            Portfolio.user_id == user.id,
        )
    )
    result = await db.execute(query)
    holding = result.scalar_one_or_none()

    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    await db.delete(holding)
    await db.commit()

    return {"success": True}


@router.get("/{portfolio_id}/analyze")
async def analyze_portfolio(
    portfolio_id: str,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze portfolio survival characteristics."""
    query = (
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
        .options(selectinload(Portfolio.holdings).selectinload(PortfolioHolding.company))
    )

    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Calculate weighted scores
    total_value = Decimal(0)
    weighted_score = Decimal(0)
    factor_totals = {
        "hard_assets": Decimal(0),
        "precious_metals": Decimal(0),
        "commodities": Decimal(0),
        "foreign_revenue": Decimal(0),
        "pricing_power": Decimal(0),
        "debt_structure": Decimal(0),
        "essential_services": Decimal(0),
    }
    scenario_totals = {"gradual": Decimal(0), "rapid": Decimal(0), "hyper": Decimal(0)}
    sector_values = {}

    for holding in portfolio.holdings:
        value = holding.current_value or Decimal(0)
        total_value += value

        # Get score
        score_query = (
            select(SurvivalScore)
            .where(SurvivalScore.company_id == holding.company_id)
            .order_by(SurvivalScore.score_date.desc())
            .limit(1)
        )
        score_result = await db.execute(score_query)
        score = score_result.scalar_one_or_none()

        if score and value > 0:
            weighted_score += value * score.total_score

            # Factor contributions
            if score.hard_assets_score:
                factor_totals["hard_assets"] += value * score.hard_assets_score
            if score.precious_metals_score:
                factor_totals["precious_metals"] += value * score.precious_metals_score
            if score.commodity_score:
                factor_totals["commodities"] += value * score.commodity_score
            if score.foreign_revenue_score:
                factor_totals["foreign_revenue"] += value * score.foreign_revenue_score
            if score.pricing_power_score:
                factor_totals["pricing_power"] += value * score.pricing_power_score
            if score.debt_structure_score:
                factor_totals["debt_structure"] += value * score.debt_structure_score
            if score.essential_services_score:
                factor_totals["essential_services"] += value * score.essential_services_score

            # Scenario contributions
            if score.scenario_gradual:
                scenario_totals["gradual"] += value * score.scenario_gradual
            if score.scenario_rapid:
                scenario_totals["rapid"] += value * score.scenario_rapid
            if score.scenario_hyper:
                scenario_totals["hyper"] += value * score.scenario_hyper

        # Sector allocation
        if holding.company and holding.company.sector:
            sector = holding.company.sector
            sector_values[sector] = sector_values.get(sector, Decimal(0)) + value

    # Calculate weighted averages
    overall_score = float(weighted_score / total_value) if total_value > 0 else None
    factor_breakdown = {
        k: round(float(v / total_value), 2) if total_value > 0 else None
        for k, v in factor_totals.items()
    }
    scenario_scores = {
        k: round(float(v / total_value), 2) if total_value > 0 else None
        for k, v in scenario_totals.items()
    }
    sector_allocation = [
        {
            "sector": sector,
            "value": float(value),
            "weight": round(float(value / total_value * 100), 2) if total_value > 0 else 0,
        }
        for sector, value in sorted(sector_values.items(), key=lambda x: -x[1])
    ]

    return {
        "portfolio": {
            "id": str(portfolio.id),
            "name": portfolio.name,
            "holdings_count": len(portfolio.holdings),
        },
        "analysis": {
            "overall_score": round(overall_score, 2) if overall_score else None,
            "total_value": float(total_value),
            "scenario_scores": scenario_scores,
            "factor_breakdown": factor_breakdown,
            "sector_allocation": sector_allocation,
        },
    }


@router.post("/{portfolio_id}/scenario")
async def run_scenario(
    portfolio_id: str,
    request: ScenarioRequest,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Run a devaluation scenario on the portfolio."""
    query = (
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
        .options(selectinload(Portfolio.holdings).selectinload(PortfolioHolding.company))
    )

    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Scenario parameters
    scenarios = {
        "gradual": {"inflation_rate": 0.05, "years": 5},
        "rapid": {"inflation_rate": 0.15, "years": 3},
        "hyper": {"inflation_rate": 0.50, "years": 2},
    }

    if request.scenario not in scenarios:
        raise HTTPException(status_code=400, detail="Invalid scenario type")

    params = request.custom_params or scenarios[request.scenario]
    inflation_rate = params.get("inflation_rate", scenarios[request.scenario]["inflation_rate"])
    years = params.get("years", scenarios[request.scenario]["years"])

    # Calculate scenario impacts
    total_value = sum(float(h.current_value or 0) for h in portfolio.holdings)
    cumulative_inflation = (1 + inflation_rate) ** years

    holdings_impact = []
    for holding in portfolio.holdings:
        value = float(holding.current_value or 0)

        # Get score for scenario adjustment
        score_query = (
            select(SurvivalScore)
            .where(SurvivalScore.company_id == holding.company_id)
            .order_by(SurvivalScore.score_date.desc())
            .limit(1)
        )
        score_result = await db.execute(score_query)
        score = score_result.scalar_one_or_none()

        # Score adjustment factor (higher score = better protection)
        scenario_score = getattr(score, f"scenario_{request.scenario}", score.total_score) if score else 50
        protection_factor = float(scenario_score or 50) / 100

        # Nominal value grows with inflation for high-score assets
        nominal_growth = 1 + (inflation_rate * protection_factor * years)
        projected_nominal = value * nominal_growth

        # Real value calculation
        projected_real = projected_nominal / cumulative_inflation

        holdings_impact.append({
            "ticker": holding.company.ticker if holding.company else None,
            "current_value": value,
            "projected_nominal": round(projected_nominal, 2),
            "projected_real": round(projected_real, 2),
            "real_change_pct": round((projected_real / value - 1) * 100, 2) if value > 0 else 0,
            "survival_score": float(scenario_score) if scenario_score else None,
        })

    # Portfolio totals
    total_nominal = sum(h["projected_nominal"] for h in holdings_impact)
    total_real = sum(h["projected_real"] for h in holdings_impact)

    return {
        "scenario": request.scenario,
        "parameters": {
            "inflation_rate": inflation_rate,
            "years": years,
            "cumulative_inflation": round(cumulative_inflation, 4),
        },
        "portfolio_impact": {
            "current_value": total_value,
            "projected_nominal": round(total_nominal, 2),
            "projected_real": round(total_real, 2),
            "real_change_pct": round((total_real / total_value - 1) * 100, 2) if total_value > 0 else 0,
        },
        "holdings_impact": holdings_impact,
    }
