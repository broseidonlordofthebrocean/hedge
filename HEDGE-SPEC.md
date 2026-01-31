# HEDGE Platform Specification

## Project Overview

**HEDGE** (Hard-asset Equity Devaluation Guard Engine) is a fullstack platform that predicts which stocks will survive US dollar devaluation scenarios. It scores equities on resilience factors like hard asset backing, precious metals exposure, foreign revenue, and pricing power.

**Core Value Proposition**: Investors can stress-test their portfolios against currency collapse scenarios and discover stocks that hedge against dollar debasement.

---

## Technical Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15+ (use Supabase or Neon for managed hosting)
- **Cache**: Redis (Upstash for serverless)
- **Task Queue**: Celery with Redis broker (or use Modal for serverless compute)
- **ORM**: SQLAlchemy 2.0 with async support

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Charts**: Recharts or Tremor
- **State**: Zustand or TanStack Query
- **Auth**: Clerk

### Mobile
- **Framework**: React Native with Expo
- **Navigation**: Expo Router
- **Shared Code**: Monorepo with shared API client and utilities

### Infrastructure
- **Web Hosting**: Vercel
- **API Hosting**: Railway or Fly.io
- **File Storage**: Cloudflare R2 or AWS S3
- **CI/CD**: GitHub Actions

---

## Project Structure

```
hedge/
├── README.md
├── docker-compose.yml           # Local dev (Postgres, Redis)
├── .github/
│   └── workflows/
│       ├── api-deploy.yml
│       ├── web-deploy.yml
│       └── test.yml
│
├── packages/
│   └── shared/                  # Shared TypeScript utilities
│       ├── package.json
│       ├── src/
│       │   ├── types/           # Shared type definitions
│       │   │   ├── company.ts
│       │   │   ├── score.ts
│       │   │   ├── portfolio.ts
│       │   │   └── index.ts
│       │   ├── utils/
│       │   │   ├── formatters.ts
│       │   │   ├── validators.ts
│       │   │   └── index.ts
│       │   └── api-client/
│       │       ├── client.ts
│       │       ├── endpoints.ts
│       │       └── index.ts
│       └── tsconfig.json
│
├── api/                         # FastAPI Backend
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── alembic/                 # Database migrations
│   │   ├── alembic.ini
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings/env vars
│   │   ├── database.py          # DB connection
│   │   │
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── company.py
│   │   │   ├── score.py
│   │   │   ├── fundamental.py
│   │   │   ├── portfolio.py
│   │   │   ├── user.py
│   │   │   └── alert.py
│   │   │
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── company.py
│   │   │   ├── score.py
│   │   │   ├── portfolio.py
│   │   │   └── screener.py
│   │   │
│   │   ├── api/                 # Route handlers
│   │   │   ├── __init__.py
│   │   │   ├── deps.py          # Dependencies (auth, db session)
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py    # Main v1 router
│   │   │   │   ├── companies.py
│   │   │   │   ├── rankings.py
│   │   │   │   ├── portfolio.py
│   │   │   │   ├── watchlist.py
│   │   │   │   ├── alerts.py
│   │   │   │   ├── screener.py
│   │   │   │   └── macro.py
│   │   │   └── health.py
│   │   │
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── scoring/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── engine.py    # Main scoring engine
│   │   │   │   ├── factors.py   # Individual factor scorers
│   │   │   │   ├── scenarios.py # Scenario modeling
│   │   │   │   └── weights.py   # Factor weight config
│   │   │   ├── portfolio/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analyzer.py
│   │   │   │   └── optimizer.py
│   │   │   └── market/
│   │   │       ├── __init__.py
│   │   │       └── macro.py     # Macro data service
│   │   │
│   │   ├── ingestion/           # Data pipeline
│   │   │   ├── __init__.py
│   │   │   ├── sec_edgar.py     # SEC filing parser
│   │   │   ├── market_data.py   # Price/quote feeds
│   │   │   ├── macro_data.py    # DXY, gold, M2, etc.
│   │   │   └── parsers/
│   │   │       ├── __init__.py
│   │   │       ├── tenk.py      # 10-K parser
│   │   │       └── tenq.py      # 10-Q parser
│   │   │
│   │   ├── tasks/               # Background jobs
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   ├── scoring.py       # Daily scoring job
│   │   │   ├── ingestion.py     # Data ingestion jobs
│   │   │   └── alerts.py        # Alert checking job
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_scoring.py
│       ├── test_api.py
│       └── test_ingestion.py
│
├── web/                         # Next.js Frontend
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   └── images/
│   │
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── globals.css
│   │   │
│   │   ├── (marketing)/         # Public marketing pages
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── pricing/
│   │   │   │   └── page.tsx
│   │   │   └── about/
│   │   │       └── page.tsx
│   │   │
│   │   ├── (auth)/              # Auth pages
│   │   │   ├── sign-in/[[...sign-in]]/
│   │   │   │   └── page.tsx
│   │   │   └── sign-up/[[...sign-up]]/
│   │   │       └── page.tsx
│   │   │
│   │   ├── (app)/               # Authenticated app
│   │   │   ├── layout.tsx       # App shell (sidebar)
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── rankings/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [sector]/
│   │   │   │       └── page.tsx
│   │   │   ├── stock/
│   │   │   │   └── [ticker]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── loading.tsx
│   │   │   ├── portfolio/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── analyze/
│   │   │   │           └── page.tsx
│   │   │   ├── screener/
│   │   │   │   └── page.tsx
│   │   │   ├── scenarios/
│   │   │   │   └── page.tsx
│   │   │   ├── watchlist/
│   │   │   │   └── page.tsx
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   │
│   │   └── api/                 # Next.js API routes (BFF)
│   │       └── [...path]/
│   │           └── route.ts     # Proxy to FastAPI
│   │
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── table.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ... (other shadcn components)
│   │   │
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── MobileNav.tsx
│   │   │
│   │   ├── charts/
│   │   │   ├── SurvivalMeter.tsx
│   │   │   ├── FactorRadar.tsx
│   │   │   ├── ScoreHistory.tsx
│   │   │   ├── MacroTicker.tsx
│   │   │   ├── SectorBreakdown.tsx
│   │   │   └── ScenarioComparison.tsx
│   │   │
│   │   ├── tables/
│   │   │   ├── RankingsTable.tsx
│   │   │   ├── HoldingsTable.tsx
│   │   │   └── WatchlistTable.tsx
│   │   │
│   │   ├── cards/
│   │   │   ├── StockCard.tsx
│   │   │   ├── FactorCard.tsx
│   │   │   ├── ScenarioCard.tsx
│   │   │   └── PortfolioSummaryCard.tsx
│   │   │
│   │   └── forms/
│   │       ├── PortfolioBuilder.tsx
│   │       ├── ScreenerFilters.tsx
│   │       ├── AlertForm.tsx
│   │       └── TickerSearch.tsx
│   │
│   ├── lib/
│   │   ├── api.ts               # API client instance
│   │   ├── utils.ts             # Utility functions
│   │   └── constants.ts
│   │
│   ├── hooks/
│   │   ├── useCompany.ts
│   │   ├── useRankings.ts
│   │   ├── usePortfolio.ts
│   │   ├── useMacro.ts
│   │   └── useScreener.ts
│   │
│   └── stores/
│       ├── portfolio.ts
│       └── screener.ts
│
└── mobile/                      # React Native App
    ├── package.json
    ├── app.json
    ├── tsconfig.json
    │
    ├── app/                     # Expo Router
    │   ├── _layout.tsx
    │   ├── index.tsx            # Home/Dashboard
    │   ├── (tabs)/
    │   │   ├── _layout.tsx
    │   │   ├── index.tsx        # Rankings tab
    │   │   ├── portfolio.tsx
    │   │   ├── watchlist.tsx
    │   │   └── settings.tsx
    │   └── stock/
    │       └── [ticker].tsx
    │
    ├── components/
    │   ├── StockListItem.tsx
    │   ├── SurvivalBadge.tsx
    │   ├── MiniChart.tsx
    │   └── PortfolioCard.tsx
    │
    └── lib/
        └── api.ts
```

---

## Database Schema

### Core Tables

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- COMPANIES
-- ============================================
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    country VARCHAR(3) DEFAULT 'USA',
    exchange VARCHAR(20),
    description TEXT,
    website VARCHAR(500),
    logo_url VARCHAR(500),
    cik VARCHAR(20),                    -- SEC CIK number
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_companies_ticker ON companies(ticker);
CREATE INDEX idx_companies_sector ON companies(sector);
CREATE INDEX idx_companies_market_cap ON companies(market_cap DESC);

-- ============================================
-- SURVIVAL SCORES
-- ============================================
CREATE TABLE survival_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    score_date DATE NOT NULL,
    
    -- Overall score (0-100)
    total_score DECIMAL(5,2) NOT NULL,
    
    -- Confidence in score (0-1) based on data completeness
    confidence DECIMAL(3,2) DEFAULT 0.5,
    
    -- Tier classification
    tier VARCHAR(20),                   -- 'excellent', 'strong', 'moderate', 'vulnerable', 'critical'
    
    -- Individual factor scores (0-100 each)
    hard_assets_score DECIMAL(5,2),
    precious_metals_score DECIMAL(5,2),
    commodity_score DECIMAL(5,2),
    foreign_revenue_score DECIMAL(5,2),
    pricing_power_score DECIMAL(5,2),
    debt_structure_score DECIMAL(5,2),
    essential_services_score DECIMAL(5,2),
    
    -- Scenario-specific scores
    scenario_gradual DECIMAL(5,2),      -- 15-20% decline over 3-5 years
    scenario_rapid DECIMAL(5,2),        -- 30-40% decline in 12-18 months
    scenario_hyper DECIMAL(5,2),        -- 50%+ hyperinflation event
    
    -- Metadata
    scoring_version VARCHAR(20),        -- Track algorithm version
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(company_id, score_date)
);

CREATE INDEX idx_scores_company_date ON survival_scores(company_id, score_date DESC);
CREATE INDEX idx_scores_date_total ON survival_scores(score_date, total_score DESC);
CREATE INDEX idx_scores_tier ON survival_scores(score_date, tier);

-- ============================================
-- COMPANY FUNDAMENTALS
-- ============================================
CREATE TABLE fundamentals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    fiscal_year INT NOT NULL,
    fiscal_quarter INT,                 -- NULL for annual, 1-4 for quarterly
    report_type VARCHAR(10),            -- '10-K', '10-Q'
    
    -- Balance Sheet
    total_assets BIGINT,
    tangible_assets BIGINT,
    intangible_assets BIGINT,
    current_assets BIGINT,
    total_liabilities BIGINT,
    total_debt BIGINT,
    cash_and_equivalents BIGINT,
    
    -- Debt Structure
    short_term_debt BIGINT,
    long_term_debt BIGINT,
    fixed_rate_debt_pct DECIMAL(5,2),
    floating_rate_debt_pct DECIMAL(5,2),
    avg_debt_maturity_years DECIMAL(4,1),
    avg_interest_rate DECIMAL(5,2),
    
    -- Revenue Breakdown
    total_revenue BIGINT,
    domestic_revenue BIGINT,
    domestic_revenue_pct DECIMAL(5,2),
    foreign_revenue BIGINT,
    foreign_revenue_pct DECIMAL(5,2),
    
    -- Geographic Revenue Detail (JSON for flexibility)
    revenue_by_region JSONB,            -- {"europe": 0.25, "asia": 0.15, ...}
    
    -- Commodity/Asset Exposure
    commodity_revenue BIGINT,
    commodity_revenue_pct DECIMAL(5,2),
    precious_metals_revenue BIGINT,
    precious_metals_revenue_pct DECIMAL(5,2),
    
    -- For Mining Companies
    proven_reserves_oz BIGINT,          -- Gold equivalent ounces
    probable_reserves_oz BIGINT,
    reserve_value_usd BIGINT,
    production_cost_per_oz DECIMAL(10,2),
    
    -- Profitability
    gross_profit BIGINT,
    gross_margin DECIMAL(5,2),
    operating_income BIGINT,
    operating_margin DECIMAL(5,2),
    net_income BIGINT,
    net_margin DECIMAL(5,2),
    
    -- Stability Metrics (calculated over rolling periods)
    gross_margin_5yr_avg DECIMAL(5,2),
    gross_margin_5yr_std DECIMAL(5,2),  -- Lower = more stable pricing power
    revenue_growth_3yr_cagr DECIMAL(5,2),
    
    -- Source
    filing_url VARCHAR(500),
    filing_date DATE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(company_id, fiscal_year, fiscal_quarter)
);

CREATE INDEX idx_fundamentals_company ON fundamentals(company_id, fiscal_year DESC, fiscal_quarter DESC);

-- ============================================
-- MACRO DATA
-- ============================================
CREATE TABLE macro_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_date DATE NOT NULL,
    
    -- Dollar Index
    dxy_value DECIMAL(10,4),
    dxy_change_1d DECIMAL(8,4),
    dxy_change_ytd DECIMAL(8,4),
    
    -- Precious Metals (USD)
    gold_price DECIMAL(10,2),
    silver_price DECIMAL(10,2),
    platinum_price DECIMAL(10,2),
    
    -- Key Commodities
    oil_wti_price DECIMAL(10,2),
    copper_price DECIMAL(10,2),
    
    -- Money Supply
    m2_supply_trillions DECIMAL(10,3),
    m2_yoy_change DECIMAL(8,4),
    
    -- Interest Rates
    fed_funds_rate DECIMAL(5,2),
    ten_year_yield DECIMAL(5,2),
    
    -- Inflation
    cpi_yoy DECIMAL(5,2),
    pce_yoy DECIMAL(5,2),
    
    -- Currency Pairs
    eur_usd DECIMAL(10,6),
    usd_jpy DECIMAL(10,4),
    gbp_usd DECIMAL(10,6),
    usd_cny DECIMAL(10,6),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(data_date)
);

CREATE INDEX idx_macro_date ON macro_data(data_date DESC);

-- ============================================
-- USER DATA (Auth handled by Clerk, this stores app data)
-- ============================================
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) UNIQUE NOT NULL,  -- From Clerk
    email VARCHAR(255),
    display_name VARCHAR(100),
    
    -- Subscription
    subscription_tier VARCHAR(20) DEFAULT 'free',  -- 'free', 'pro', 'team', 'enterprise'
    subscription_status VARCHAR(20) DEFAULT 'active',
    stripe_customer_id VARCHAR(255),
    subscription_ends_at TIMESTAMPTZ,
    
    -- Preferences
    preferences JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_clerk_id ON user_profiles(clerk_user_id);

-- ============================================
-- PORTFOLIOS
-- ============================================
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_primary BOOLEAN DEFAULT false,
    
    -- Cached aggregate scores (updated on change)
    total_value DECIMAL(15,2),
    survival_score DECIMAL(5,2),
    scenario_gradual_score DECIMAL(5,2),
    scenario_rapid_score DECIMAL(5,2),
    scenario_hyper_score DECIMAL(5,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_portfolios_user ON portfolios(user_id);

CREATE TABLE portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id),
    
    shares DECIMAL(15,4) NOT NULL,
    cost_basis DECIMAL(15,2),           -- Total cost basis
    cost_per_share DECIMAL(15,4),
    
    -- Cached current values (updated periodically)
    current_price DECIMAL(15,4),
    current_value DECIMAL(15,2),
    gain_loss DECIMAL(15,2),
    gain_loss_pct DECIMAL(8,4),
    
    notes TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(portfolio_id, company_id)
);

CREATE INDEX idx_holdings_portfolio ON portfolio_holdings(portfolio_id);

-- ============================================
-- WATCHLISTS
-- ============================================
CREATE TABLE watchlist_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id),
    
    notes TEXT,
    target_score DECIMAL(5,2),          -- Alert when score reaches this
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, company_id)
);

CREATE INDEX idx_watchlist_user ON watchlist_items(user_id);

-- ============================================
-- ALERTS
-- ============================================
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id),  -- NULL for portfolio-level alerts
    portfolio_id UUID REFERENCES portfolios(id),
    
    alert_type VARCHAR(50) NOT NULL,    -- 'score_drop', 'score_rise', 'threshold', 'new_filing', 'macro_trigger'
    
    -- Conditions
    threshold_value DECIMAL(10,2),
    threshold_direction VARCHAR(10),    -- 'above', 'below', 'change'
    change_percent DECIMAL(5,2),        -- For percent change alerts
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_triggered_at TIMESTAMPTZ,
    trigger_count INT DEFAULT 0,
    
    -- Notification preferences
    notify_email BOOLEAN DEFAULT true,
    notify_push BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_user ON alerts(user_id, is_active);
CREATE INDEX idx_alerts_company ON alerts(company_id) WHERE company_id IS NOT NULL;

-- ============================================
-- API KEYS (for paid API access)
-- ============================================
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    key_hash VARCHAR(255) NOT NULL,     -- Hashed API key
    key_prefix VARCHAR(10) NOT NULL,    -- First 8 chars for identification
    name VARCHAR(100),
    
    -- Rate limiting
    rate_limit_per_hour INT DEFAULT 100,
    rate_limit_per_month INT DEFAULT 10000,
    
    -- Usage tracking
    requests_this_hour INT DEFAULT 0,
    requests_this_month INT DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix);

-- ============================================
-- SCORING AUDIT LOG
-- ============================================
CREATE TABLE scoring_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_date DATE NOT NULL,
    
    -- Stats
    companies_scored INT,
    companies_failed INT,
    avg_score DECIMAL(5,2),
    median_score DECIMAL(5,2),
    
    -- Performance
    duration_seconds INT,
    scoring_version VARCHAR(20),
    
    -- Status
    status VARCHAR(20),                 -- 'running', 'completed', 'failed'
    error_message TEXT,
    
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

---

## API Specification

### Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://api.hedge.finance/v1`

### Authentication
- Public endpoints: No auth required
- Protected endpoints: Bearer token (JWT from Clerk)
- API access: `X-API-Key` header

### Endpoints

#### Health & Status
```
GET /health
Response: { "status": "healthy", "version": "1.0.0", "timestamp": "..." }

GET /status
Response: { 
    "companies_tracked": 847,
    "last_scoring_run": "2024-01-15T06:00:00Z",
    "macro_data_updated": "2024-01-15T14:30:00Z"
}
```

#### Companies
```
GET /companies
Query params:
    - page (int, default 1)
    - limit (int, default 50, max 100)
    - sector (string, optional)
    - min_score (float, optional)
    - max_score (float, optional)
    - search (string, optional - searches ticker and name)
    - sort_by (string: 'score', 'ticker', 'market_cap', 'name')
    - sort_order (string: 'asc', 'desc')
Response: {
    "data": [CompanyWithScore],
    "pagination": { "page": 1, "limit": 50, "total": 847, "pages": 17 }
}

GET /companies/:ticker
Response: CompanyDetail (includes current score, fundamentals, history)

GET /companies/:ticker/scores
Query params:
    - start_date (date, optional)
    - end_date (date, optional)
    - limit (int, default 30)
Response: { "data": [ScoreHistory] }

GET /companies/:ticker/fundamentals
Query params:
    - years (int, default 5)
Response: { "data": [Fundamental] }

GET /companies/:ticker/peers
Response: { "data": [CompanyWithScore] }  // Same sector, similar market cap

GET /companies/search
Query params:
    - q (string, required, min 1 char)
    - limit (int, default 10)
Response: { "data": [{ ticker, name, sector, score }] }
```

#### Rankings
```
GET /rankings
Query params:
    - limit (int, default 100)
    - sector (string, optional)
    - tier (string: 'excellent', 'strong', 'moderate', 'vulnerable', 'critical')
    - scenario (string: 'current', 'gradual', 'rapid', 'hyper')
Response: {
    "data": [RankedCompany],
    "generated_at": "2024-01-15T06:00:00Z",
    "total_analyzed": 847
}

GET /rankings/sectors
Response: {
    "data": [
        { "sector": "Gold Mining", "avg_score": 91.2, "count": 12 },
        ...
    ]
}

GET /rankings/movers
Query params:
    - period (string: '1d', '7d', '30d')
    - direction (string: 'up', 'down', 'both')
    - limit (int, default 20)
Response: {
    "gainers": [{ company, score_change, current_score }],
    "losers": [{ company, score_change, current_score }]
}

GET /rankings/tiers
Response: {
    "excellent": { "min": 85, "max": 100, "count": 45 },
    "strong": { "min": 70, "max": 84.99, "count": 123 },
    ...
}
```

#### Screener
```
POST /screener
Body: {
    "filters": {
        "sectors": ["Gold Mining", "Energy"],
        "min_score": 70,
        "max_score": 100,
        "min_market_cap": 1000000000,
        "max_market_cap": null,
        "min_foreign_revenue_pct": 40,
        "min_hard_assets_score": 60,
        "min_precious_metals_score": 50,
        "has_dividend": true,
        "countries": ["USA", "CAN"]
    },
    "sort_by": "total_score",
    "sort_order": "desc",
    "page": 1,
    "limit": 50
}
Response: {
    "data": [CompanyWithScore],
    "pagination": {...},
    "filter_summary": { "matched": 34, "total_universe": 847 }
}

GET /screener/presets
Response: {
    "data": [
        { "id": "gold_bugs", "name": "Gold Bugs", "description": "...", "filters": {...} },
        { "id": "inflation_hedge", "name": "Inflation Hedges", ... },
        ...
    ]
}
```

#### Portfolio (Protected)
```
GET /portfolio
Response: { "data": [PortfolioSummary] }

POST /portfolio
Body: { "name": "My Retirement", "description": "..." }
Response: Portfolio

GET /portfolio/:id
Response: PortfolioDetail (with holdings, scores, analysis)

PUT /portfolio/:id
Body: { "name": "...", "description": "..." }
Response: Portfolio

DELETE /portfolio/:id
Response: { "success": true }

POST /portfolio/:id/holdings
Body: { 
    "ticker": "NEM",
    "shares": 100,
    "cost_basis": 4500.00
}
Response: Holding

PUT /portfolio/:id/holdings/:holding_id
Body: { "shares": 150, "cost_basis": 6750.00 }
Response: Holding

DELETE /portfolio/:id/holdings/:holding_id
Response: { "success": true }

GET /portfolio/:id/analyze
Response: {
    "portfolio": PortfolioDetail,
    "analysis": {
        "overall_score": 72.5,
        "weighted_by_value": 68.3,
        "scenario_scores": {
            "gradual": 74.1,
            "rapid": 65.2,
            "hyper": 58.9
        },
        "factor_breakdown": {
            "hard_assets": { "score": 65, "weight_in_portfolio": 0.35 },
            ...
        },
        "sector_allocation": [...],
        "risk_concentrations": [
            { "type": "sector", "name": "Financials", "pct": 45, "warning": "High exposure to vulnerable sector" }
        ],
        "recommendations": [
            { "action": "reduce", "ticker": "JPM", "reason": "Low survival score in rapid scenario" },
            { "action": "add", "ticker": "NEM", "reason": "Increase precious metals exposure" }
        ]
    }
}

POST /portfolio/:id/scenario
Body: {
    "scenario": "rapid",  // or custom
    "custom_params": {     // optional, for custom scenarios
        "dollar_decline_pct": 35,
        "timeline_months": 18,
        "inflation_rate": 15
    }
}
Response: {
    "scenario": "rapid",
    "portfolio_impact": {
        "current_value": 150000,
        "projected_nominal": 142000,
        "projected_real": 98000,
        "survival_score": 65.2
    },
    "holdings_impact": [
        { "ticker": "NEM", "current_value": 10000, "projected_change_pct": 45 },
        ...
    ]
}
```

#### Watchlist (Protected)
```
GET /watchlist
Response: { "data": [WatchlistItem] }

POST /watchlist
Body: { "ticker": "GOLD", "notes": "Watch for breakout" }
Response: WatchlistItem

DELETE /watchlist/:company_id
Response: { "success": true }
```

#### Alerts (Protected)
```
GET /alerts
Response: { "data": [Alert] }

POST /alerts
Body: {
    "company_id": "uuid" | null,
    "portfolio_id": "uuid" | null,
    "alert_type": "score_drop",
    "threshold_value": 70,
    "threshold_direction": "below",
    "notify_email": true,
    "notify_push": true
}
Response: Alert

PUT /alerts/:id
Body: { ... }
Response: Alert

DELETE /alerts/:id
Response: { "success": true }
```

#### Macro Data
```
GET /macro/current
Response: {
    "data": MacroData,
    "updated_at": "2024-01-15T14:30:00Z"
}

GET /macro/history
Query params:
    - start_date (date)
    - end_date (date)
    - metrics (comma-separated: 'dxy,gold,m2')
Response: { "data": [MacroDataPoint] }

GET /macro/dashboard
Response: {
    "dxy": { "current": 98.42, "change_1d": -0.5, "change_ytd": -12.4 },
    "gold": { "current": 2847, "change_1d": 1.2, "change_ytd": 18.5 },
    "silver": { "current": 32.50, ... },
    "m2": { "current": 21.3, "yoy_change": 8.2 },
    "rates": { "fed_funds": 5.25, "ten_year": 4.15 },
    "updated_at": "..."
}
```

---

## Scoring Engine Specification

### Factor Weights (Default)

| Factor | Weight | Description |
|--------|--------|-------------|
| Hard Assets | 25% | Tangible assets / total assets ratio |
| Precious Metals | 15% | Direct gold/silver/platinum exposure |
| Commodities | 15% | Non-PM commodity production/revenue |
| Foreign Revenue | 15% | % revenue from non-USD markets |
| Pricing Power | 15% | Gross margin stability over time |
| Debt Structure | 10% | Fixed rate %, maturity, currency |
| Essential Services | 5% | Sector-based demand inelasticity |

### Factor Scoring Logic

#### Hard Assets Score (0-100)
```python
def score_hard_assets(fundamentals):
    if not fundamentals.total_assets:
        return 50  # Neutral if unknown
    
    tangible_ratio = fundamentals.tangible_assets / fundamentals.total_assets
    
    # Boost for specific hard asset types
    real_estate_boost = 10 if has_significant_real_estate(fundamentals) else 0
    inventory_boost = 5 if has_commodity_inventory(fundamentals) else 0
    
    base_score = tangible_ratio * 100
    return min(base_score + real_estate_boost + inventory_boost, 100)
```

#### Precious Metals Score (0-100)
```python
def score_precious_metals(company, fundamentals):
    # Direct miners get top scores
    if company.industry in ['Gold Mining', 'Silver Mining', 'Precious Metals']:
        reserve_factor = min(fundamentals.proven_reserves_oz / 10_000_000, 1) * 20
        return min(80 + reserve_factor, 100)
    
    # Royalty/streaming companies
    if company.industry == 'Precious Metals Royalties':
        return 85
    
    # Other companies: based on PM revenue exposure
    pm_revenue_pct = fundamentals.precious_metals_revenue_pct or 0
    return min(pm_revenue_pct * 2, 100)
```

#### Commodity Score (0-100)
```python
def score_commodities(company, fundamentals):
    commodity_sectors = {
        'Oil & Gas E&P': 85,
        'Oil & Gas Integrated': 80,
        'Copper Mining': 85,
        'Diversified Mining': 75,
        'Agricultural Products': 70,
        'Steel': 65,
        'Chemicals': 55,
    }
    
    sector_base = commodity_sectors.get(company.industry, 30)
    
    # Adjust based on actual commodity revenue
    commodity_pct = fundamentals.commodity_revenue_pct or 0
    revenue_adjustment = (commodity_pct - 50) * 0.3  # +/- 15 points
    
    return max(0, min(sector_base + revenue_adjustment, 100))
```

#### Foreign Revenue Score (0-100)
```python
def score_foreign_revenue(fundamentals):
    foreign_pct = fundamentals.foreign_revenue_pct or 0
    
    # Linear scale with slight boost for very high international
    if foreign_pct >= 70:
        return 95
    elif foreign_pct >= 50:
        return 70 + (foreign_pct - 50) * 1.25
    else:
        return foreign_pct * 1.4
```

#### Pricing Power Score (0-100)
```python
def score_pricing_power(fundamentals):
    margin = fundamentals.gross_margin or 0
    stability = fundamentals.gross_margin_5yr_std or 10  # Default to moderate variance
    
    # High margin = can absorb cost increases
    margin_score = min(margin * 1.2, 50)
    
    # Low variance = consistent pricing power
    stability_score = max(50 - (stability * 5), 0)
    
    return margin_score + stability_score
```

#### Debt Structure Score (0-100)
```python
def score_debt_structure(fundamentals):
    # Fixed rate debt is good (inflates away)
    fixed_pct = fundamentals.fixed_rate_debt_pct or 50
    fixed_score = fixed_pct * 0.5  # 0-50 points
    
    # Longer maturity is good
    maturity = fundamentals.avg_debt_maturity_years or 5
    maturity_score = min(maturity * 5, 30)  # 0-30 points
    
    # Low debt/assets ratio is good
    if fundamentals.total_assets and fundamentals.total_debt:
        debt_ratio = fundamentals.total_debt / fundamentals.total_assets
        leverage_score = max(20 - (debt_ratio * 40), 0)  # 0-20 points
    else:
        leverage_score = 10
    
    return fixed_score + maturity_score + leverage_score
```

#### Essential Services Score (0-100)
```python
ESSENTIAL_SCORES = {
    'Electric Utilities': 95,
    'Water Utilities': 95,
    'Gas Utilities': 90,
    'Healthcare Facilities': 90,
    'Pharmaceuticals': 85,
    'Food Products': 85,
    'Food Retail': 80,
    'Household Products': 75,
    'Waste Management': 75,
    'Telecom': 70,
    'Defense': 70,
    'Insurance': 40,
    'Banks': 35,
    'Asset Management': 30,
    'Software': 25,
    'Consumer Discretionary': 20,
}

def score_essential_services(company):
    return ESSENTIAL_SCORES.get(company.industry, 40)
```

### Scenario Modeling

```python
def calculate_scenario_scores(factor_scores, scenario):
    """
    Adjust factor weights based on devaluation scenario severity.
    More severe scenarios weight hard assets and PM higher.
    """
    
    if scenario == 'gradual':
        # Balanced - all factors matter
        weights = {
            'hard_assets': 0.25,
            'precious_metals': 0.15,
            'commodities': 0.15,
            'foreign_revenue': 0.15,
            'pricing_power': 0.15,
            'debt_structure': 0.10,
            'essential_services': 0.05,
        }
    
    elif scenario == 'rapid':
        # Hard assets and PM matter more
        weights = {
            'hard_assets': 0.30,
            'precious_metals': 0.25,
            'commodities': 0.20,
            'foreign_revenue': 0.10,
            'pricing_power': 0.10,
            'debt_structure': 0.05,
            'essential_services': 0.00,
        }
    
    elif scenario == 'hyper':
        # Only real assets matter
        weights = {
            'hard_assets': 0.35,
            'precious_metals': 0.35,
            'commodities': 0.20,
            'foreign_revenue': 0.05,
            'pricing_power': 0.05,
            'debt_structure': 0.00,
            'essential_services': 0.00,
        }
    
    return sum(
        factor_scores[factor] * weight 
        for factor, weight in weights.items()
    )
```

### Tier Classification

| Tier | Score Range | Description |
|------|-------------|-------------|
| Excellent | 85-100 | Strong survivors, likely to outperform |
| Strong | 70-84 | Good positioning, moderate risk |
| Moderate | 55-69 | Mixed factors, scenario-dependent |
| Vulnerable | 40-54 | Significant exposure to devaluation |
| Critical | 0-39 | High risk of underperformance |

---

## Data Ingestion Specification

### SEC EDGAR Integration

```python
# Target filings
FILING_TYPES = ['10-K', '10-Q']

# Data points to extract from filings
EXTRACTION_TARGETS = {
    '10-K': {
        'balance_sheet': [
            'total_assets',
            'total_current_assets', 
            'property_plant_equipment_net',
            'intangible_assets',
            'total_liabilities',
            'long_term_debt',
            'short_term_debt',
        ],
        'income_statement': [
            'total_revenue',
            'cost_of_revenue',
            'gross_profit',
            'operating_income',
            'net_income',
        ],
        'geographic_revenue': True,  # Parse geographic segment data
        'debt_schedule': True,        # Parse debt maturity schedule
    }
}

# Parsing approach
# 1. Download filing from EDGAR
# 2. Parse XBRL if available (structured data)
# 3. Fall back to HTML/text parsing for older filings
# 4. Use LLM assistance for complex extractions (geographic segments)
```

### Market Data Sources

```python
# Primary: Polygon.io or Alpha Vantage
# Backup: Yahoo Finance (yfinance)

MARKET_DATA_ENDPOINTS = {
    'quotes': 'Real-time/delayed quotes',
    'company_info': 'Company details, sector, industry',
    'financials': 'Quarterly/annual financials (backup to SEC)',
}

# Update frequency
MARKET_DATA_SCHEDULE = {
    'quotes': '15min during market hours',
    'company_info': 'daily',
    'financials': 'on filing release',
}
```

### Macro Data Sources

```python
MACRO_SOURCES = {
    'dxy': {
        'source': 'FRED or TradingView',
        'ticker': 'DTWEXBGS',
        'frequency': 'hourly',
    },
    'gold': {
        'source': 'Polygon or Yahoo',
        'ticker': 'GC=F',
        'frequency': '15min',
    },
    'silver': {
        'source': 'Polygon or Yahoo', 
        'ticker': 'SI=F',
        'frequency': '15min',
    },
    'm2': {
        'source': 'FRED',
        'ticker': 'M2SL',
        'frequency': 'weekly (Thursday release)',
    },
    'fed_funds': {
        'source': 'FRED',
        'ticker': 'FEDFUNDS',
        'frequency': 'daily',
    },
    'cpi': {
        'source': 'FRED',
        'ticker': 'CPIAUCSL',
        'frequency': 'monthly',
    },
}
```

---

## UI/UX Specification

### Design System

#### Colors
```css
:root {
    /* Base */
    --black: #0a0a0a;
    --charcoal: #141414;
    --slate: #1a1a1a;
    
    /* Gold accent (primary) */
    --gold: #d4a853;
    --gold-dim: #8b7235;
    --gold-bright: #f5d485;
    
    /* Status colors */
    --green: #2d8a4e;
    --green-bright: #4ade80;
    --red: #c73434;
    --red-dim: #8a2424;
    
    /* Text */
    --text: #e8e8e8;
    --text-dim: #6b6b6b;
    --text-muted: #4a4a4a;
    
    /* Borders */
    --border: #2a2a2a;
    --border-hover: #3a3a3a;
}
```

#### Typography
```css
/* Headlines */
font-family: 'Bebas Neue', sans-serif;
letter-spacing: 0.05-0.1em;

/* Data/Mono */
font-family: 'JetBrains Mono', monospace;

/* Body */
font-family: 'Source Serif 4', Georgia, serif;
```

#### Score Tier Colors
```css
.score-excellent { color: #4ade80; }  /* Green */
.score-strong { color: #22d3ee; }     /* Cyan */
.score-moderate { color: #d4a853; }   /* Gold */
.score-vulnerable { color: #f97316; } /* Orange */
.score-critical { color: #c73434; }   /* Red */
```

### Key Components

#### Survival Meter
- Horizontal bar showing 0-100 score
- Color gradient based on tier
- Animated fill on load
- Tooltip with factor breakdown

#### Factor Radar Chart
- 7-axis radar showing individual factor scores
- Overlay comparison (vs. sector avg, vs. benchmark)
- Interactive hover for details

#### Rankings Table
- Sortable columns
- Quick-filter pills (sector, tier)
- Infinite scroll or pagination
- Row click → stock detail
- Inline sparkline for score history

#### Macro Ticker
- Horizontal scrolling tape
- DXY, Gold, Silver, M2, Fed Funds
- Color-coded changes (green/red)
- Click to expand history chart

#### Portfolio Analyzer
- Donut chart: sector allocation
- Stacked bar: factor contribution
- Scenario toggle: see scores change
- Risk warnings highlighted
- Recommendation cards

### Page Layouts

#### Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ [Macro Ticker - scrolling]                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Portfolio Score │  │ Top Movers (24h)            │  │
│  │      72.5       │  │ ▲ GOLD +3.2  ▼ JPM -2.1    │  │
│  │ [Mini Radar]    │  │ ▲ NEM +2.8   ▼ BAC -1.9    │  │
│  └─────────────────┘  └─────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Your Holdings                              [Edit] │ │
│  │ ┌─────┬─────────┬────────┬───────┐              │ │
│  │ │Rank │ Ticker  │ Value  │ Score │              │ │
│  │ ├─────┼─────────┼────────┼───────┤              │ │
│  │ │ 1   │ NEM     │ $10.2k │ 94    │              │ │
│  │ │ 2   │ XOM     │ $8.5k  │ 88    │              │ │
│  │ └─────┴─────────┴────────┴───────┘              │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Stock Detail
```
┌─────────────────────────────────────────────────────────┐
│ ← Back to Rankings                                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  NEM                                    [+ Watchlist]   │
│  Newmont Corporation                    [+ Portfolio]   │
│  NYSE · Gold Mining · $45.2B                           │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │         SURVIVAL SCORE                          │   │
│  │              94                                  │   │
│  │    ████████████████████████░░░  EXCELLENT      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Gradual     │  │ Rapid       │  │ Hyper       │    │
│  │    92       │  │    96       │  │    98       │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  Factor Breakdown                                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [Radar Chart]              │ Hard Assets    87 │   │
│  │                            │ Precious Met.  98 │   │
│  │                            │ Commodities    85 │   │
│  │                            │ Foreign Rev.   72 │   │
│  │                            │ Pricing Power  68 │   │
│  │                            │ Debt Structure 75 │   │
│  │                            │ Essential Svc  45 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Score History (90 days)                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [Line Chart]                                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Testing Requirements

### Unit Tests
- Scoring engine: all factor calculations
- API endpoints: request/response validation
- Data parsers: SEC filing extraction

### Integration Tests
- Database operations
- External API integrations (mocked)
- Auth flow

### E2E Tests (Playwright)
- User registration → portfolio creation → analysis
- Search → stock detail → add to watchlist
- Screener filters → results → export

### Performance Benchmarks
- Scoring run: < 5 min for full universe
- API response: < 200ms p95
- Page load: < 2s LCP

---

## Deployment Configuration

### Environment Variables

```env
# API
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
CORS_ORIGINS=https://hedge.finance,http://localhost:3000

# External APIs
POLYGON_API_KEY=...
FRED_API_KEY=...
SEC_USER_AGENT=HEDGE contact@hedge.finance

# Auth
CLERK_SECRET_KEY=...
CLERK_WEBHOOK_SECRET=...

# Payments
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...

# Web
NEXT_PUBLIC_API_URL=https://api.hedge.finance
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=...
```

### Docker Compose (Local Dev)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: hedge
      POSTGRES_PASSWORD: hedge_dev
      POSTGRES_DB: hedge
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://hedge:hedge_dev@postgres:5432/hedge
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./api:/app

  web:
    build: ./web
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    volumes:
      - ./web:/app
      - /app/node_modules

volumes:
  postgres_data:
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Project scaffolding (monorepo setup)
- [ ] Database schema + migrations
- [ ] Basic FastAPI structure
- [ ] Core models and schemas
- [ ] Health endpoints
- [ ] Docker compose for local dev
- [ ] Seed data: S&P 500 companies (manual)

### Phase 2: Scoring Engine (Week 3)
- [ ] Factor scoring implementations
- [ ] Scenario modeling
- [ ] Tier classification
- [ ] Unit tests for scoring
- [ ] Manual scoring run capability

### Phase 3: API Layer (Week 4)
- [ ] Companies endpoints
- [ ] Rankings endpoints
- [ ] Screener endpoint
- [ ] Macro data endpoint
- [ ] API documentation (OpenAPI)

### Phase 4: Data Pipeline (Week 5-6)
- [ ] SEC EDGAR integration
- [ ] Market data integration
- [ ] Macro data feeds
- [ ] Scheduled jobs (Celery)
- [ ] Automated daily scoring

### Phase 5: Web Frontend (Week 7-9)
- [ ] Next.js setup + Tailwind + shadcn
- [ ] Marketing pages (landing, pricing)
- [ ] Auth integration (Clerk)
- [ ] Dashboard page
- [ ] Rankings page
- [ ] Stock detail page
- [ ] Screener page

### Phase 6: User Features (Week 10-11)
- [ ] Portfolio management
- [ ] Watchlist
- [ ] Portfolio analysis
- [ ] Scenario comparison

### Phase 7: Premium Features (Week 12-13)
- [ ] Alerts system
- [ ] Stripe integration
- [ ] Subscription tiers
- [ ] API key management
- [ ] Rate limiting

### Phase 8: Mobile App (Week 14-16)
- [ ] Expo setup
- [ ] Core screens (rankings, detail, portfolio)
- [ ] Push notifications
- [ ] App store submission

### Phase 9: Polish & Launch (Week 17-18)
- [ ] Performance optimization
- [ ] Error handling & logging
- [ ] Analytics integration
- [ ] Documentation
- [ ] Beta testing
- [ ] Production deployment

---

## Success Metrics

### Product
- 1,000 registered users in first month
- 100 paid subscribers in first quarter
- < 1% churn rate

### Technical
- 99.9% API uptime
- < 200ms API response time (p95)
- Daily scoring runs complete by 6:30 AM ET
- Zero data loss incidents

### Business
- $5k MRR by month 6
- 10 enterprise inquiries by month 6
- Featured in 2+ financial publications

---

## Open Questions / Decisions Needed

1. **Data provider**: Polygon.io vs Alpha Vantage vs other?
2. **Hosting**: Vercel + Railway vs AWS vs other?
3. **Mobile priority**: Launch with web-only MVP or include mobile?
4. **Pricing tiers**: Finalize feature gates per tier
5. **Legal**: Disclaimer language, terms of service review
6. **Brand**: Final name (HEDGE vs other), domain acquisition

---

## Appendix

### Sample Companies for Testing

```
Tier: Excellent (85+)
- NEM (Newmont) - Gold mining
- GOLD (Barrick) - Gold mining
- FCX (Freeport) - Copper mining
- XOM (Exxon) - Oil major

Tier: Strong (70-84)
- CAT (Caterpillar) - Industrials
- DE (Deere) - Agriculture
- MO (Altria) - Consumer staples

Tier: Moderate (55-69)
- PG (P&G) - Consumer staples
- JNJ (J&J) - Healthcare

Tier: Vulnerable (40-54)
- JPM (JPMorgan) - Financials
- BAC (Bank of America) - Financials

Tier: Critical (<40)
- Regional banks
- Pure-play SaaS with no hard assets
```

### Glossary

- **DXY**: US Dollar Index (trade-weighted basket)
- **M2**: Broad money supply measure
- **Hard Assets**: Tangible assets (property, equipment, inventory)
- **Pricing Power**: Ability to raise prices without losing customers
- **Survival Score**: Composite 0-100 rating of devaluation resilience
