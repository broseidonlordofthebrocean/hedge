# HEDGE

A comprehensive financial analytics and portfolio management platform designed to help investors make data-driven decisions through advanced stock screening, ranking algorithms, and portfolio tracking.

## Tech Stack

- **Backend**: Python / FastAPI
- **Frontend**: Next.js (React)
- **Database**: PostgreSQL
- **Cache**: Redis

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose

The fastest way to get started is with Docker Compose:

```bash
# Clone the repository
git clone https://github.com/your-org/hedge.git
cd hedge

# Start all services
docker-compose up -d

# The application will be available at:
# - Web: http://localhost:3000
# - API: http://localhost:8000
```

### API Setup (Local Development)

```bash
# Navigate to the API directory
cd api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --port 8000
```

### Web Setup (Local Development)

```bash
# Navigate to the web directory
cd web

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Start the development server
npm run dev
```

## Project Structure

```
hedge/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core configuration
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── alembic/           # Database migrations
│   └── tests/             # API tests
├── web/                    # Next.js frontend
│   ├── app/               # App router pages
│   │   ├── (app)/         # Authenticated app routes
│   │   ├── (auth)/        # Authentication routes
│   │   └── (marketing)/   # Public marketing pages
│   ├── components/        # React components
│   ├── lib/               # Utility functions
│   └── public/            # Static assets
├── docker-compose.yml      # Docker orchestration
└── README.md
```

## License

MIT
