"""Authentication service using Clerk."""

import logging
from typing import Optional
import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ClerkAuthService:
    """Service for Clerk authentication."""

    CLERK_API_URL = "https://api.clerk.com/v1"

    def __init__(self):
        self.secret_key = settings.clerk_secret_key

    async def verify_session(self, session_token: str) -> Optional[dict]:
        """Verify a Clerk session token."""
        if not self.secret_key:
            logger.warning("Clerk secret key not configured")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.CLERK_API_URL}/tokens/verify",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                        "Content-Type": "application/json",
                    },
                    json={"token": session_token},
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Session verification failed: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Error verifying session: {e}")
            return None

    async def get_user(self, user_id: str) -> Optional[dict]:
        """Get user details from Clerk."""
        if not self.secret_key:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.CLERK_API_URL}/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                    },
                )

                if response.status_code == 200:
                    return response.json()
                return None

        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email address."""
        if not self.secret_key:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.CLERK_API_URL}/users",
                    headers={
                        "Authorization": f"Bearer {self.secret_key}",
                    },
                    params={"email_address": email},
                )

                if response.status_code == 200:
                    users = response.json()
                    if users and len(users) > 0:
                        return users[0]
                return None

        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None


def decode_clerk_jwt(token: str) -> Optional[dict]:
    """Decode a Clerk JWT without verification (for extracting claims)."""
    import base64
    import json

    try:
        # Split the token
        parts = token.split(".")
        if len(parts) != 3:
            return None

        # Decode the payload (second part)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding

        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)

    except Exception as e:
        logger.error(f"Error decoding JWT: {e}")
        return None
