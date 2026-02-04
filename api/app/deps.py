"""FastAPI dependencies."""

from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .models import UserProfile, ApiKey
from .services.auth import ClerkAuthService, decode_clerk_jwt


async def get_current_user_id(
    authorization: Optional[str] = Header(None),
) -> Optional[str]:
    """Extract user ID from Clerk JWT token."""
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]
    claims = decode_clerk_jwt(token)

    if not claims:
        return None

    return claims.get("sub")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    user_id: Optional[str] = Depends(get_current_user_id),
) -> Optional[UserProfile]:
    """Get current authenticated user from database."""
    if not user_id:
        return None

    result = await db.execute(
        select(UserProfile).where(UserProfile.clerk_id == user_id)
    )
    return result.scalar_one_or_none()


async def require_user(
    user: Optional[UserProfile] = Depends(get_current_user),
) -> UserProfile:
    """Require authenticated user, raise 401 if not authenticated."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_pro_user(
    user: UserProfile = Depends(require_user),
) -> UserProfile:
    """Require Pro tier user."""
    if user.subscription_tier not in ["pro", "institutional"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro subscription required",
        )
    return user


async def require_institutional_user(
    user: UserProfile = Depends(require_user),
) -> UserProfile:
    """Require Institutional tier user."""
    if user.subscription_tier != "institutional":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institutional subscription required",
        )
    return user


async def get_api_key_user(
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserProfile]:
    """Authenticate via API key."""
    if not x_api_key:
        return None

    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key_hash == x_api_key,  # In production, hash the key
            ApiKey.is_active == True,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        return None

    # Update last used
    from datetime import datetime
    api_key.last_used_at = datetime.utcnow()
    api_key.request_count = (api_key.request_count or 0) + 1
    await db.commit()

    # Get user
    user_result = await db.execute(
        select(UserProfile).where(UserProfile.id == api_key.user_id)
    )
    return user_result.scalar_one_or_none()


async def get_authenticated_user(
    jwt_user: Optional[UserProfile] = Depends(get_current_user),
    api_key_user: Optional[UserProfile] = Depends(get_api_key_user),
) -> Optional[UserProfile]:
    """Get user from either JWT or API key authentication."""
    return jwt_user or api_key_user


async def require_authenticated_user(
    user: Optional[UserProfile] = Depends(get_authenticated_user),
) -> UserProfile:
    """Require authentication via JWT or API key."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user
