"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Companies table
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('ticker', sa.String(10), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('sector', sa.String(100)),
        sa.Column('industry', sa.String(100)),
        sa.Column('market_cap', sa.BigInteger),
        sa.Column('country', sa.String(3), server_default='USA'),
        sa.Column('exchange', sa.String(20)),
        sa.Column('description', sa.Text),
        sa.Column('website', sa.String(500)),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('cik', sa.String(20)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_companies_ticker', 'companies', ['ticker'])
    op.create_index('idx_companies_sector', 'companies', ['sector'])
    op.create_index('idx_companies_market_cap', 'companies', ['market_cap'], postgresql_using='btree')

    # Survival scores table
    op.create_table(
        'survival_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('score_date', sa.Date, nullable=False),
        sa.Column('total_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('confidence', sa.Numeric(3, 2), server_default='0.5'),
        sa.Column('tier', sa.String(20)),
        sa.Column('hard_assets_score', sa.Numeric(5, 2)),
        sa.Column('precious_metals_score', sa.Numeric(5, 2)),
        sa.Column('commodity_score', sa.Numeric(5, 2)),
        sa.Column('foreign_revenue_score', sa.Numeric(5, 2)),
        sa.Column('pricing_power_score', sa.Numeric(5, 2)),
        sa.Column('debt_structure_score', sa.Numeric(5, 2)),
        sa.Column('essential_services_score', sa.Numeric(5, 2)),
        sa.Column('scenario_gradual', sa.Numeric(5, 2)),
        sa.Column('scenario_rapid', sa.Numeric(5, 2)),
        sa.Column('scenario_hyper', sa.Numeric(5, 2)),
        sa.Column('scoring_version', sa.String(20)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('company_id', 'score_date', name='uq_company_score_date'),
    )
    op.create_index('idx_scores_company_date', 'survival_scores', ['company_id', 'score_date'])
    op.create_index('idx_scores_date_total', 'survival_scores', ['score_date', 'total_score'])
    op.create_index('idx_scores_tier', 'survival_scores', ['score_date', 'tier'])

    # Fundamentals table
    op.create_table(
        'fundamentals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fiscal_year', sa.Integer, nullable=False),
        sa.Column('fiscal_quarter', sa.Integer),
        sa.Column('report_type', sa.String(10)),
        sa.Column('total_assets', sa.BigInteger),
        sa.Column('tangible_assets', sa.BigInteger),
        sa.Column('intangible_assets', sa.BigInteger),
        sa.Column('current_assets', sa.BigInteger),
        sa.Column('total_liabilities', sa.BigInteger),
        sa.Column('total_debt', sa.BigInteger),
        sa.Column('cash_and_equivalents', sa.BigInteger),
        sa.Column('short_term_debt', sa.BigInteger),
        sa.Column('long_term_debt', sa.BigInteger),
        sa.Column('fixed_rate_debt_pct', sa.Numeric(5, 2)),
        sa.Column('floating_rate_debt_pct', sa.Numeric(5, 2)),
        sa.Column('avg_debt_maturity_years', sa.Numeric(4, 1)),
        sa.Column('avg_interest_rate', sa.Numeric(5, 2)),
        sa.Column('total_revenue', sa.BigInteger),
        sa.Column('domestic_revenue', sa.BigInteger),
        sa.Column('domestic_revenue_pct', sa.Numeric(5, 2)),
        sa.Column('foreign_revenue', sa.BigInteger),
        sa.Column('foreign_revenue_pct', sa.Numeric(5, 2)),
        sa.Column('revenue_by_region', postgresql.JSONB),
        sa.Column('commodity_revenue', sa.BigInteger),
        sa.Column('commodity_revenue_pct', sa.Numeric(5, 2)),
        sa.Column('precious_metals_revenue', sa.BigInteger),
        sa.Column('precious_metals_revenue_pct', sa.Numeric(5, 2)),
        sa.Column('proven_reserves_oz', sa.BigInteger),
        sa.Column('probable_reserves_oz', sa.BigInteger),
        sa.Column('reserve_value_usd', sa.BigInteger),
        sa.Column('production_cost_per_oz', sa.Numeric(10, 2)),
        sa.Column('gross_profit', sa.BigInteger),
        sa.Column('gross_margin', sa.Numeric(5, 2)),
        sa.Column('operating_income', sa.BigInteger),
        sa.Column('operating_margin', sa.Numeric(5, 2)),
        sa.Column('net_income', sa.BigInteger),
        sa.Column('net_margin', sa.Numeric(5, 2)),
        sa.Column('gross_margin_5yr_avg', sa.Numeric(5, 2)),
        sa.Column('gross_margin_5yr_std', sa.Numeric(5, 2)),
        sa.Column('revenue_growth_3yr_cagr', sa.Numeric(5, 2)),
        sa.Column('filing_url', sa.String(500)),
        sa.Column('filing_date', sa.Date),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('company_id', 'fiscal_year', 'fiscal_quarter', name='uq_company_fiscal_period'),
    )
    op.create_index('idx_fundamentals_company', 'fundamentals', ['company_id', 'fiscal_year', 'fiscal_quarter'])

    # Macro data table
    op.create_table(
        'macro_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('data_date', sa.Date, nullable=False, unique=True),
        sa.Column('dxy_value', sa.Numeric(10, 4)),
        sa.Column('dxy_change_1d', sa.Numeric(8, 4)),
        sa.Column('dxy_change_ytd', sa.Numeric(8, 4)),
        sa.Column('gold_price', sa.Numeric(10, 2)),
        sa.Column('silver_price', sa.Numeric(10, 2)),
        sa.Column('platinum_price', sa.Numeric(10, 2)),
        sa.Column('oil_wti_price', sa.Numeric(10, 2)),
        sa.Column('copper_price', sa.Numeric(10, 2)),
        sa.Column('m2_supply_trillions', sa.Numeric(10, 3)),
        sa.Column('m2_yoy_change', sa.Numeric(8, 4)),
        sa.Column('fed_funds_rate', sa.Numeric(5, 2)),
        sa.Column('ten_year_yield', sa.Numeric(5, 2)),
        sa.Column('cpi_yoy', sa.Numeric(5, 2)),
        sa.Column('pce_yoy', sa.Numeric(5, 2)),
        sa.Column('eur_usd', sa.Numeric(10, 6)),
        sa.Column('usd_jpy', sa.Numeric(10, 4)),
        sa.Column('gbp_usd', sa.Numeric(10, 6)),
        sa.Column('usd_cny', sa.Numeric(10, 6)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_macro_date', 'macro_data', ['data_date'])

    # User profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('clerk_user_id', sa.String(255), nullable=False, unique=True),
        sa.Column('email', sa.String(255)),
        sa.Column('display_name', sa.String(100)),
        sa.Column('subscription_tier', sa.String(20), server_default='free'),
        sa.Column('subscription_status', sa.String(20), server_default='active'),
        sa.Column('stripe_customer_id', sa.String(255)),
        sa.Column('subscription_ends_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('preferences', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_users_clerk_id', 'user_profiles', ['clerk_user_id'])

    # Portfolios table
    op.create_table(
        'portfolios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('is_primary', sa.Boolean, server_default='false'),
        sa.Column('total_value', sa.Numeric(15, 2)),
        sa.Column('survival_score', sa.Numeric(5, 2)),
        sa.Column('scenario_gradual_score', sa.Numeric(5, 2)),
        sa.Column('scenario_rapid_score', sa.Numeric(5, 2)),
        sa.Column('scenario_hyper_score', sa.Numeric(5, 2)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_portfolios_user', 'portfolios', ['user_id'])

    # Portfolio holdings table
    op.create_table(
        'portfolio_holdings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('shares', sa.Numeric(15, 4), nullable=False),
        sa.Column('cost_basis', sa.Numeric(15, 2)),
        sa.Column('cost_per_share', sa.Numeric(15, 4)),
        sa.Column('current_price', sa.Numeric(15, 4)),
        sa.Column('current_value', sa.Numeric(15, 2)),
        sa.Column('gain_loss', sa.Numeric(15, 2)),
        sa.Column('gain_loss_pct', sa.Numeric(8, 4)),
        sa.Column('notes', sa.Text),
        sa.Column('added_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('portfolio_id', 'company_id', name='uq_portfolio_company'),
    )
    op.create_index('idx_holdings_portfolio', 'portfolio_holdings', ['portfolio_id'])

    # Watchlist items table
    op.create_table(
        'watchlist_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('notes', sa.Text),
        sa.Column('target_score', sa.Numeric(5, 2)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('user_id', 'company_id', name='uq_user_watchlist_company'),
    )
    op.create_index('idx_watchlist_user', 'watchlist_items', ['user_id'])

    # Alerts table
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id')),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('portfolios.id')),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('threshold_value', sa.Numeric(10, 2)),
        sa.Column('threshold_direction', sa.String(10)),
        sa.Column('change_percent', sa.Numeric(5, 2)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_triggered_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('trigger_count', sa.Integer, server_default='0'),
        sa.Column('notify_email', sa.Boolean, server_default='true'),
        sa.Column('notify_push', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_alerts_user', 'alerts', ['user_id', 'is_active'])
    op.create_index('idx_alerts_company', 'alerts', ['company_id'], postgresql_where=sa.text('company_id IS NOT NULL'))

    # API keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False),
        sa.Column('key_prefix', sa.String(10), nullable=False),
        sa.Column('name', sa.String(100)),
        sa.Column('rate_limit_per_hour', sa.Integer, server_default='100'),
        sa.Column('rate_limit_per_month', sa.Integer, server_default='10000'),
        sa.Column('requests_this_hour', sa.Integer, server_default='0'),
        sa.Column('requests_this_month', sa.Integer, server_default='0'),
        sa.Column('last_used_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_api_keys_user', 'api_keys', ['user_id'])
    op.create_index('idx_api_keys_prefix', 'api_keys', ['key_prefix'])

    # Scoring runs table
    op.create_table(
        'scoring_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('run_date', sa.Date, nullable=False),
        sa.Column('companies_scored', sa.Integer),
        sa.Column('companies_failed', sa.Integer),
        sa.Column('avg_score', sa.Numeric(5, 2)),
        sa.Column('median_score', sa.Numeric(5, 2)),
        sa.Column('duration_seconds', sa.Integer),
        sa.Column('scoring_version', sa.String(20)),
        sa.Column('status', sa.String(20)),
        sa.Column('error_message', sa.Text),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table('scoring_runs')
    op.drop_table('api_keys')
    op.drop_table('alerts')
    op.drop_table('watchlist_items')
    op.drop_table('portfolio_holdings')
    op.drop_table('portfolios')
    op.drop_table('user_profiles')
    op.drop_table('macro_data')
    op.drop_table('fundamentals')
    op.drop_table('survival_scores')
    op.drop_table('companies')
