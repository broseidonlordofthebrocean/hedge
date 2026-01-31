# CLAUDE.md - Execution Guide for HEDGE Platform

## Project Context

You are building **HEDGE** (Hard-asset Equity Devaluation Guard Engine), a fullstack platform that scores stocks on their resilience to US dollar devaluation. The complete specification is in `HEDGE-SPEC.md`.

## Existing Repository

**This project takes over an existing git repository.** Do not create a new repo or re-initialize git.

Before starting:
1. Check the current state of the repo (`git status`, `git log --oneline -10`)
2. Review any existing files/structure in the project root
3. Ask the user if there's anything that should be preserved or migrated
4. Create a new branch for the HEDGE implementation: `git checkout -b hedge-platform`

If there are existing files that conflict with the HEDGE structure:
- Ask before overwriting/removing
- Move legacy files to a `/legacy` folder if the user wants to keep them
- Document what was changed in the commit message

The user may have additional context about the existing project — ask if unclear.

## Quick Reference

### Tech Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, PostgreSQL, Redis, Celery
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Mobile**: React Native + Expo (Phase 8)
- **Auth**: Clerk
- **Payments**: Stripe

### Project Structure
```
hedge/
├── api/          # FastAPI backend
├── web/          # Next.js frontend
├── mobile/       # React Native app (later phase)
├── packages/
│   └── shared/   # Shared TypeScript types/utils
├── docker-compose.yml
└── HEDGE-SPEC.md
```

## Build Commands

### Initial Setup
```bash
# Assess existing repo first
git status
ls -la

# Create feature branch
git checkout -b hedge-platform

# Create structure (in existing repo root)
mkdir -p api web packages/shared/src mobile

# API setup
cd api
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install fastapi uvicorn sqlalchemy[asyncio] asyncpg alembic pydantic-settings redis celery httpx pytest pytest-asyncio
pip freeze > requirements.txt

# Web setup  
cd ../
npx create-next-app@latest web --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"
cd web
npx shadcn@latest init
npx shadcn@latest add button card input table dialog dropdown-menu

# Shared package
cd ../
mkdir -p packages/shared/src
cd packages/shared
npm init -y
```

### Development
```bash
# Start all services
docker-compose up -d postgres redis

# API (from /api)
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Web (from /web)
npm run dev

# Run migrations (from /api)
alembic upgrade head

# Run tests
pytest
```

### Production Build
```bash
# API
docker build -t hedge-api ./api

# Web
cd web && npm run build
```

## Implementation Order

Follow this sequence. Each step should result in working, tested code before moving to the next.

### Step 1: Project Assessment & Scaffolding

**First, assess the existing repository:**
```bash
# Check current state
git status
git log --oneline -10
ls -la
```

Ask the user:
- What existing files should be preserved?
- Any existing functionality to migrate?
- Preferred branch strategy?

**Then scaffold the HEDGE structure:**
- Create branch: `git checkout -b hedge-platform`
- Create directory structure as specified (without overwriting user-approved files)
- Initialize `docker-compose.yml` for local Postgres and Redis
- Update `.gitignore` for Python + Node

**Deliverables:**
- [ ] Existing repo assessed and documented
- [ ] New branch created
- [ ] Directory structure created (merged with existing if needed)
- [ ] `docker-compose.yml` working
- [ ] Can connect to local Postgres
- [ ] Clean `.gitignore` covering all tech

### Step 2: Database Schema
Implement the full schema from HEDGE-SPEC.md using Alembic migrations.

**Files to create:**
- `api/app/database.py` - async SQLAlchemy setup
- `api/app/models/*.py` - all SQLAlchemy models
- `api/alembic/versions/001_initial.py` - migration

**Validation:**
```bash
alembic upgrade head
# Verify all tables exist in Postgres
```

### Step 3: Pydantic Schemas
Create request/response schemas matching the API spec.

**Files to create:**
- `api/app/schemas/company.py`
- `api/app/schemas/score.py`
- `api/app/schemas/portfolio.py`
- `api/app/schemas/screener.py`
- `api/app/schemas/macro.py`

### Step 4: Scoring Engine
Implement the core scoring logic. This is the heart of the product.

**Files to create:**
- `api/app/services/scoring/weights.py` - factor weight config
- `api/app/services/scoring/factors.py` - individual factor scorers
- `api/app/services/scoring/scenarios.py` - scenario modeling
- `api/app/services/scoring/engine.py` - main orchestrator

**Test thoroughly:**
```python
# Test with known inputs
def test_gold_miner_scores_high():
    company = CompanyData(
        ticker="NEM",
        sector="Gold Mining",
        fundamentals={
            "tangible_assets": 30_000_000_000,
            "total_assets": 35_000_000_000,
            "proven_reserves_oz": 100_000_000,
            ...
        }
    )
    result = scorer.score(company)
    assert result["total_score"] >= 85
    assert result["factors"]["precious_metals"] >= 90
```

### Step 5: Core API Endpoints
Implement the read-only public endpoints first.

**Priority order:**
1. `GET /health` - simple health check
2. `GET /companies` - list with pagination
3. `GET /companies/:ticker` - single company detail
4. `GET /rankings` - sorted by score
5. `GET /macro/dashboard` - current macro data

**Files to create:**
- `api/app/api/deps.py` - database session dependency
- `api/app/api/v1/companies.py`
- `api/app/api/v1/rankings.py`
- `api/app/api/v1/macro.py`
- `api/app/api/v1/router.py` - combine all routers

### Step 6: Seed Data
Create a seed script to populate initial data for development.

**File:** `api/scripts/seed.py`

Include at minimum:
- 50 companies across different sectors
- Manual fundamentals data for 10 key stocks
- 30 days of mock macro data
- Pre-calculated scores

```bash
python scripts/seed.py
```

### Step 7: Next.js Foundation
Set up the web app with proper structure and design system.

**Files to create:**
- `web/app/globals.css` - design tokens from spec
- `web/app/layout.tsx` - root layout with fonts
- `web/lib/api.ts` - API client
- `web/components/layout/Header.tsx`
- `web/components/layout/Footer.tsx`

**Fonts to install:**
```bash
npm install @fontsource/bebas-neue @fontsource/jetbrains-mono @fontsource/source-serif-4
```

### Step 8: Marketing Pages
Build the public-facing landing page.

**Files:**
- `web/app/(marketing)/layout.tsx`
- `web/app/(marketing)/page.tsx` - landing page (use the HTML from earlier as reference)
- `web/app/(marketing)/pricing/page.tsx`

**The landing page should include:**
- Hero with value prop
- Live macro ticker (mocked initially)
- Sample rankings preview
- Factor explanation
- Pricing tiers
- CTA to sign up

### Step 9: App Shell
Create the authenticated app layout.

**Files:**
- `web/app/(app)/layout.tsx` - sidebar + header
- `web/components/layout/Sidebar.tsx`
- `web/components/layout/AppHeader.tsx`

### Step 10: Dashboard Page
Main dashboard after login.

**Files:**
- `web/app/(app)/dashboard/page.tsx`
- `web/components/charts/MacroTicker.tsx`
- `web/components/cards/PortfolioSummaryCard.tsx`

### Step 11: Rankings Page
Full rankings table with filtering.

**Files:**
- `web/app/(app)/rankings/page.tsx`
- `web/components/tables/RankingsTable.tsx`
- `web/components/charts/SurvivalMeter.tsx`
- `web/hooks/useRankings.ts`

### Step 12: Stock Detail Page
Individual stock analysis view.

**Files:**
- `web/app/(app)/stock/[ticker]/page.tsx`
- `web/components/charts/FactorRadar.tsx`
- `web/components/charts/ScoreHistory.tsx`
- `web/components/cards/FactorCard.tsx`

### Step 13: Auth Integration
Add Clerk authentication.

```bash
npm install @clerk/nextjs
```

**Files:**
- `web/app/(auth)/sign-in/[[...sign-in]]/page.tsx`
- `web/app/(auth)/sign-up/[[...sign-up]]/page.tsx`
- `web/middleware.ts` - protect app routes
- `api/app/api/deps.py` - add auth dependency

### Step 14: Portfolio Management
User portfolios (requires auth).

**API endpoints:**
- All `/portfolio/*` routes

**Web pages:**
- `web/app/(app)/portfolio/page.tsx`
- `web/app/(app)/portfolio/[id]/page.tsx`
- `web/components/forms/PortfolioBuilder.tsx`
- `web/components/tables/HoldingsTable.tsx`

### Step 15: Portfolio Analysis
The key premium feature.

**Files:**
- `api/app/services/portfolio/analyzer.py`
- `web/app/(app)/portfolio/[id]/analyze/page.tsx`
- `web/components/charts/SectorBreakdown.tsx`
- `web/components/charts/ScenarioComparison.tsx`

### Step 16: Screener
Advanced filtering interface.

**Files:**
- `api/app/api/v1/screener.py`
- `web/app/(app)/screener/page.tsx`
- `web/components/forms/ScreenerFilters.tsx`
- `web/stores/screener.ts`

### Step 17: Data Ingestion Pipeline
Automate data collection.

**Files:**
- `api/app/ingestion/sec_edgar.py`
- `api/app/ingestion/market_data.py`
- `api/app/ingestion/macro_data.py`
- `api/app/tasks/celery_app.py`
- `api/app/tasks/scoring.py`
- `api/app/tasks/ingestion.py`

### Step 18: Alerts & Watchlist
User notification features.

**API:**
- `/watchlist/*` endpoints
- `/alerts/*` endpoints

**Web:**
- `web/app/(app)/watchlist/page.tsx`
- Alert configuration in settings

### Step 19: Payments
Stripe subscription integration.

```bash
npm install stripe @stripe/stripe-js
pip install stripe
```

**Files:**
- `api/app/api/v1/billing.py`
- `web/app/(app)/settings/billing/page.tsx`
- Webhook handler for subscription events

### Step 20: Mobile App (Optional)
React Native implementation.

```bash
npx create-expo-app mobile
cd mobile
npx expo install expo-router
```

## Code Style Guidelines

### Python (API)
```python
# Use async everywhere
async def get_company(db: AsyncSession, ticker: str) -> Company | None:
    result = await db.execute(
        select(Company).where(Company.ticker == ticker)
    )
    return result.scalar_one_or_none()

# Type hints required
def calculate_score(
    fundamentals: dict[str, Any],
    weights: FactorWeights
) -> ScoringResult:
    ...

# Docstrings for public functions
def score_hard_assets(fundamentals: Fundamentals) -> Decimal:
    """
    Calculate hard asset score based on tangible/total asset ratio.
    
    Returns a score from 0-100 where higher indicates more hard asset backing.
    """
    ...
```

### TypeScript (Web)
```typescript
// Use interfaces for API responses
interface Company {
  id: string;
  ticker: string;
  name: string;
  sector: string;
  score: number;
}

// Typed hooks
function useCompany(ticker: string) {
  return useQuery<Company>({
    queryKey: ['company', ticker],
    queryFn: () => api.getCompany(ticker),
  });
}

// Component props interfaces
interface SurvivalMeterProps {
  score: number;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}
```

### CSS/Tailwind
```tsx
// Use design tokens from globals.css
<div className="bg-charcoal border border-border text-text">
  <h1 className="font-display text-gold">Score</h1>
  <p className="font-mono text-text-dim">94</p>
</div>

// Component-specific styles in same file
const tierColors = {
  excellent: 'text-green-400',
  strong: 'text-cyan-400', 
  moderate: 'text-gold',
  vulnerable: 'text-orange-500',
  critical: 'text-red-500',
} as const;
```

## Common Patterns

### API Error Handling
```python
from fastapi import HTTPException

async def get_company_or_404(db: AsyncSession, ticker: str) -> Company:
    company = await get_company(db, ticker)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")
    return company
```

### Database Queries
```python
# Pagination
async def list_companies(
    db: AsyncSession,
    page: int = 1,
    limit: int = 50,
    sector: str | None = None,
) -> tuple[list[Company], int]:
    query = select(Company).where(Company.is_active == True)
    
    if sector:
        query = query.where(Company.sector == sector)
    
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    # Get page
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    
    return result.scalars().all(), total
```

### React Query Setup
```typescript
// lib/api.ts
const api = {
  async getCompanies(params: CompanyListParams) {
    const res = await fetch(`${API_URL}/companies?${new URLSearchParams(params)}`);
    if (!res.ok) throw new Error('Failed to fetch');
    return res.json();
  },
  // ...
};

// hooks/useCompanies.ts
export function useCompanies(params: CompanyListParams) {
  return useQuery({
    queryKey: ['companies', params],
    queryFn: () => api.getCompanies(params),
  });
}
```

## Testing Checklist

Before considering any feature complete:

- [ ] Unit tests pass
- [ ] API returns correct status codes
- [ ] Error cases handled gracefully
- [ ] Loading states implemented
- [ ] Mobile responsive (web)
- [ ] No TypeScript errors
- [ ] No console errors in browser

## Environment Setup

### Required Environment Variables

**API (.env)**
```
DATABASE_URL=postgresql+asyncpg://hedge:hedge_dev@localhost:5432/hedge
REDIS_URL=redis://localhost:6379
SECRET_KEY=dev-secret-change-in-prod
CORS_ORIGINS=http://localhost:3000
POLYGON_API_KEY=your_key
FRED_API_KEY=your_key
```

**Web (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

## Deployment Notes

### API (Railway/Fly.io)
- Use production Postgres (Supabase/Neon)
- Set all env vars in dashboard
- Health check endpoint: `/health`
- Auto-deploy from `main` branch

### Web (Vercel)
- Connect to GitHub repo
- Set env vars in project settings
- Build command: `npm run build`
- Output directory: `.next`

## Quick Fixes

### Common Issues

**CORS errors:**
```python
# api/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Database connection issues:**
```python
# Ensure async driver
DATABASE_URL=postgresql+asyncpg://...  # Note the +asyncpg
```

**Clerk auth not working:**
```typescript
// middleware.ts
export default clerkMiddleware();
export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Next.js App Router](https://nextjs.org/docs/app)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Clerk Next.js](https://clerk.com/docs/quickstarts/nextjs)
- [SEC EDGAR API](https://www.sec.gov/search-filings)
- [FRED API](https://fred.stlouisfed.org/docs/api/fred/)
