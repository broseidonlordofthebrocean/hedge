"""Billing API v1 endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...deps import require_user
from ...models import UserProfile
from ...services.billing import BillingService, get_tier_from_price_id, TIER_PRICES

router = APIRouter()
billing_service = BillingService()


class CheckoutRequest(BaseModel):
    tier: str  # "pro" or "institutional"
    interval: str  # "monthly" or "yearly"
    success_url: str
    cancel_url: str


class PortalRequest(BaseModel):
    return_url: str


@router.get("/prices")
async def get_prices():
    """Get available subscription prices."""
    return {
        "tiers": {
            "free": {
                "name": "Free",
                "price": 0,
                "features": [
                    "Access to top 10 ranked companies",
                    "Basic macro dashboard",
                    "Weekly email digest",
                ],
            },
            "pro": {
                "name": "Pro",
                "monthly_price": TIER_PRICES["pro"]["monthly"],
                "yearly_price": TIER_PRICES["pro"]["yearly"],
                "features": [
                    "Full rankings access",
                    "Real-time macro data",
                    "Custom screener filters",
                    "Portfolio tracking (up to 3)",
                    "Custom alerts",
                    "API access (1000 calls/month)",
                ],
            },
            "institutional": {
                "name": "Institutional",
                "monthly_price": TIER_PRICES["institutional"]["monthly"],
                "yearly_price": TIER_PRICES["institutional"]["yearly"],
                "features": [
                    "Everything in Pro",
                    "Unlimited portfolios",
                    "Priority data updates",
                    "API access (unlimited)",
                    "Custom factor weights",
                    "Dedicated support",
                    "Bulk export",
                ],
            },
        },
    }


@router.post("/checkout")
async def create_checkout_session(
    request: CheckoutRequest,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe Checkout session for subscription."""
    if request.tier not in ["pro", "institutional"]:
        raise HTTPException(status_code=400, detail="Invalid tier")
    if request.interval not in ["monthly", "yearly"]:
        raise HTTPException(status_code=400, detail="Invalid interval")

    price_id = f"price_{request.tier}_{request.interval}"

    # Create Stripe customer if needed
    if not user.stripe_customer_id:
        customer_id = await billing_service.create_customer(
            email=user.email,
            name=user.full_name,
        )
        user.stripe_customer_id = customer_id
        await db.commit()
    else:
        customer_id = user.stripe_customer_id

    checkout_url = await billing_service.create_checkout_session(
        customer_id=customer_id,
        price_id=price_id,
        success_url=request.success_url,
        cancel_url=request.cancel_url,
    )

    return {"checkout_url": checkout_url}


@router.post("/portal")
async def create_portal_session(
    request: PortalRequest,
    user: UserProfile = Depends(require_user),
):
    """Create a Stripe Customer Portal session."""
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found")

    portal_url = await billing_service.create_portal_session(
        customer_id=user.stripe_customer_id,
        return_url=request.return_url,
    )

    return {"portal_url": portal_url}


@router.get("/subscription")
async def get_subscription(
    user: UserProfile = Depends(require_user),
):
    """Get current subscription details."""
    if not user.stripe_subscription_id:
        return {
            "tier": user.subscription_tier or "free",
            "status": "active" if user.subscription_tier == "free" else None,
            "subscription": None,
        }

    subscription = await billing_service.get_subscription(user.stripe_subscription_id)

    return {
        "tier": user.subscription_tier,
        "status": subscription.get("status") if subscription else None,
        "subscription": subscription,
    }


@router.post("/cancel")
async def cancel_subscription(
    user: UserProfile = Depends(require_user),
):
    """Cancel subscription at end of billing period."""
    if not user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    success = await billing_service.cancel_subscription(
        user.stripe_subscription_id,
        at_period_end=True,
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")

    return {"status": "canceling", "message": "Subscription will cancel at end of billing period"}


@router.post("/reactivate")
async def reactivate_subscription(
    user: UserProfile = Depends(require_user),
):
    """Reactivate a subscription that was set to cancel."""
    if not user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No subscription to reactivate")

    success = await billing_service.reactivate_subscription(user.stripe_subscription_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to reactivate subscription")

    return {"status": "active", "message": "Subscription reactivated"}
