"""User API v1 endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...deps import require_user, get_current_user_id
from ...models import UserProfile
from ...services.auth import ClerkAuthService

router = APIRouter()
auth_service = ClerkAuthService()


class UserCreate(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    notification_preferences: Optional[dict] = None


class UserResponse(BaseModel):
    id: str
    clerk_id: str
    email: str
    full_name: Optional[str]
    subscription_tier: str
    api_calls_remaining: int

    class Config:
        from_attributes = True


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    user: UserProfile = Depends(require_user),
):
    """Get current user profile."""
    return user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    updates: UserUpdate,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""
    if updates.full_name is not None:
        user.full_name = updates.full_name
    if updates.notification_preferences is not None:
        user.notification_preferences = updates.notification_preferences

    await db.commit()
    await db.refresh(user)
    return user


@router.post("/sync")
async def sync_clerk_user(
    clerk_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Sync user from Clerk to local database (called on first login)."""
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Check if user already exists
    result = await db.execute(
        select(UserProfile).where(UserProfile.clerk_id == clerk_id)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return {"status": "exists", "user_id": str(existing_user.id)}

    # Get user info from Clerk
    clerk_user = await auth_service.get_user(clerk_id)
    if not clerk_user:
        raise HTTPException(status_code=400, detail="Could not fetch user from Clerk")

    # Create local user
    email = None
    if clerk_user.get("email_addresses"):
        primary_email = next(
            (e for e in clerk_user["email_addresses"] if e.get("id") == clerk_user.get("primary_email_address_id")),
            clerk_user["email_addresses"][0] if clerk_user["email_addresses"] else None,
        )
        if primary_email:
            email = primary_email.get("email_address")

    if not email:
        raise HTTPException(status_code=400, detail="User has no email address")

    user = UserProfile(
        clerk_id=clerk_id,
        email=email,
        full_name=f"{clerk_user.get('first_name', '')} {clerk_user.get('last_name', '')}".strip() or None,
        subscription_tier="free",
        api_calls_remaining=100,
    )
    db.add(user)
    await db.commit()

    return {"status": "created", "user_id": str(user.id)}


@router.get("/api-keys")
async def list_api_keys(
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's API keys."""
    from ...models import ApiKey

    result = await db.execute(
        select(ApiKey).where(
            ApiKey.user_id == user.id,
            ApiKey.is_active == True,
        )
    )
    keys = result.scalars().all()

    return {
        "keys": [
            {
                "id": str(key.id),
                "name": key.name,
                "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
                "request_count": key.request_count,
                "created_at": key.created_at.isoformat() if key.created_at else None,
            }
            for key in keys
        ]
    }


@router.post("/api-keys")
async def create_api_key(
    name: str,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new API key."""
    import secrets
    from ...models import ApiKey

    # Check tier limits
    if user.subscription_tier not in ["pro", "institutional"]:
        raise HTTPException(status_code=403, detail="API access requires Pro subscription")

    # Check existing key count
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.user_id == user.id,
            ApiKey.is_active == True,
        )
    )
    existing_keys = result.scalars().all()

    max_keys = 3 if user.subscription_tier == "pro" else 10
    if len(existing_keys) >= max_keys:
        raise HTTPException(status_code=400, detail=f"Maximum {max_keys} API keys allowed")

    # Generate key
    key_value = f"hedge_{secrets.token_urlsafe(32)}"

    api_key = ApiKey(
        user_id=user.id,
        name=name,
        key_hash=key_value,  # In production, store hash instead
        is_active=True,
    )
    db.add(api_key)
    await db.commit()

    return {
        "key": key_value,
        "id": str(api_key.id),
        "name": name,
        "message": "Store this key securely. It will not be shown again.",
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    user: UserProfile = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke an API key."""
    from ...models import ApiKey

    result = await db.execute(
        select(ApiKey).where(
            ApiKey.id == key_id,
            ApiKey.user_id == user.id,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.is_active = False
    await db.commit()

    return {"status": "revoked"}
