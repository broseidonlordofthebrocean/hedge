"""Stripe billing service."""

import logging
from typing import Optional
import stripe

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Stripe
stripe.api_key = settings.stripe_secret_key

# Product/Price IDs (configure in Stripe Dashboard)
PRICE_IDS = {
    "pro_monthly": "price_pro_monthly",
    "pro_yearly": "price_pro_yearly",
    "institutional_monthly": "price_institutional_monthly",
    "institutional_yearly": "price_institutional_yearly",
}

TIER_PRICES = {
    "pro": {"monthly": 29, "yearly": 290},
    "institutional": {"monthly": 199, "yearly": 1990},
}


class BillingService:
    """Service for Stripe billing operations."""

    async def create_customer(self, email: str, name: Optional[str] = None) -> str:
        """Create a Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
            )
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Error creating customer: {e}")
            raise

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create a Stripe Checkout session."""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Error creating checkout session: {e}")
            raise

    async def create_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> str:
        """Create a Stripe Customer Portal session."""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Error creating portal session: {e}")
            raise

    async def get_subscription(self, subscription_id: str) -> Optional[dict]:
        """Get subscription details."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "plan": subscription.items.data[0].price.id if subscription.items.data else None,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error getting subscription: {e}")
            return None

    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> bool:
        """Cancel a subscription."""
        try:
            if at_period_end:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
            else:
                stripe.Subscription.delete(subscription_id)
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Error canceling subscription: {e}")
            return False

    async def reactivate_subscription(self, subscription_id: str) -> bool:
        """Reactivate a subscription that was set to cancel."""
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False,
            )
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Error reactivating subscription: {e}")
            return False

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> stripe.Event:
        """Construct and verify a webhook event."""
        webhook_secret = settings.stripe_webhook_secret
        return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)


def get_tier_from_price_id(price_id: str) -> Optional[str]:
    """Map Stripe price ID to subscription tier."""
    if "pro" in price_id.lower():
        return "pro"
    elif "institutional" in price_id.lower():
        return "institutional"
    return None
