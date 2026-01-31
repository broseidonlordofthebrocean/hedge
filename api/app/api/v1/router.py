from fastapi import APIRouter

from .companies import router as companies_router
from .rankings import router as rankings_router
from .screener import router as screener_router
from .macro import router as macro_router
from .portfolio import router as portfolio_router
from .watchlist import router as watchlist_router
from .alerts import router as alerts_router

api_router = APIRouter()

api_router.include_router(companies_router, prefix="/companies", tags=["Companies"])
api_router.include_router(rankings_router, prefix="/rankings", tags=["Rankings"])
api_router.include_router(screener_router, prefix="/screener", tags=["Screener"])
api_router.include_router(macro_router, prefix="/macro", tags=["Macro"])
api_router.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(watchlist_router, prefix="/watchlist", tags=["Watchlist"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
