from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
import uuid

from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.activity import ActivityCompletionRequest, ActivityCompletionResponse
from app.models.activity_completion import ActivityCompletion
from app.models.transaction import Transaction, CurrencyType
from app.models.user import User
from app.core.constants import (
    ActivityType,
    EURO_REWARD_WORKSHEET, EURO_REWARD_QUIZ, EURO_REWARD_CYP,
    EURO_REWARD_PODCAST_BASE, EURO_REWARD_PODCAST_ENGAGED,
    EURO_REWARD_VIDEO_BASE, EURO_REWARD_VIDEO_DISTRACTED,
    PODCAST_ENGAGEMENT_THRESHOLD_SECONDS, VIDEO_FOCUS_INTERRUPTION_THRESHOLD
)


router = APIRouter(prefix="/activities", tags=["activities"])


def calculate_euros_awarded(activity_type: ActivityType, request: ActivityCompletionRequest) -> int:
    """Calculate euros awarded based on activity type and frontend payload."""
    if activity_type in (ActivityType.WORKSHEET, ActivityType.QUIZ, ActivityType.CYP):
        return EURO_REWARD_WORKSHEET  # All base activities give 10 euros
    
    elif activity_type == ActivityType.PODCAST:
        # Podcasts: base 2 euros, 4 euros if foreground_time_seconds > 180
        if request.foreground_time_seconds is not None and request.foreground_time_seconds > PODCAST_ENGAGEMENT_THRESHOLD_SECONDS:
            return EURO_REWARD_PODCAST_ENGAGED
        return EURO_REWARD_PODCAST_BASE
    
    elif activity_type == ActivityType.VIDEO:
        # Videos: requires completed=True and focus_interruptions
        # Base 5 euros, reduced to 2 euros if interruptions > 3
        if request.completed is not True:
            # If not completed, no euros awarded
            return 0
        
        if request.focus_interruptions is not None and request.focus_interruptions > VIDEO_FOCUS_INTERRUPTION_THRESHOLD:
            return EURO_REWARD_VIDEO_DISTRACTED
        return EURO_REWARD_VIDEO_BASE
    
    return 0


@router.post("/complete", response_model=ActivityCompletionResponse)
async def complete_activity(
    request: ActivityCompletionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Record an activity completion and award Euros via a Transaction with FOR UPDATE locking.
    Endpoint is idempotent: if the (user_id, resource_id, activity_type) tuple already exists, 
    the existing record is returned.
    
    Implements proper earning mechanics based on activity type and frontend payload.
    Uses SELECT FOR UPDATE to prevent race conditions during concurrent requests.
    """

    # Normalize UUIDs
    try:
        resource_uuid = uuid.UUID(str(request.resource_id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resource_id")

    # Calculate euros awarded based on activity type and payload
    euros_awarded = calculate_euros_awarded(request.activity_type, request)
    
    # Determine reason based on activity type and conditions
    reason_parts = [request.activity_type.value.replace('_', ' ').title()]
    if request.activity_type == ActivityType.PODCAST:
        if request.foreground_time_seconds is not None and request.foreground_time_seconds > PODCAST_ENGAGEMENT_THRESHOLD_SECONDS:
            reason_parts.append("(engaged listening)")
        else:
            reason_parts.append("(standard)")
    elif request.activity_type == ActivityType.VIDEO:
        if request.completed is not True:
            reason_parts.append("(not completed)")
        elif request.focus_interruptions is not None and request.focus_interruptions > VIDEO_FOCUS_INTERRUPTION_THRESHOLD:
            reason_parts.append("(distracted)")
        else:
            reason_parts.append("(focused)")
    
    reason = " ".join(reason_parts) + " completion"

    # Use SELECT FOR UPDATE to lock the user's balance row for the transaction
    # This prevents race conditions when multiple requests try to update the same user's balance
    user_query = select(User).where(User.id == current_user.id).with_for_update()
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Create transaction and activity completion inside a transaction
    tx = Transaction(
        user_id=user.id,
        currency_type=CurrencyType.EUROS,
        amount=euros_awarded,
        reason=reason,
    )

    if euros_awarded > 0:
        user.euros_balance += euros_awarded
        user.lifetime_euros += euros_awarded

    db.add(tx)

    try:
        # Flush to get transaction.id for FK
        await db.flush()

        ac = ActivityCompletion(
            user_id=user.id,
            resource_id=resource_uuid,
            activity_type=request.activity_type,
            euros_awarded=euros_awarded,
            transaction_id=tx.id,
        )
        db.add(ac)
        await db.commit()
        await db.refresh(ac)
        return ac

    except IntegrityError as err:
        # Unique constraint violation implies the activity was already recorded.
        await db.rollback()
        # Try to fetch the existing record and return it (idempotent behavior)
        existing_q = select(ActivityCompletion).where(
            ActivityCompletion.user_id == user.id,
            ActivityCompletion.resource_id == resource_uuid,
            ActivityCompletion.activity_type == request.activity_type,
        )
        existing_res = await db.execute(existing_q)
        existing = existing_res.scalars().first()
        if existing is not None:
            return existing

        # If we can't find it, re-raise as a 409 to indicate conflict
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Activity completion conflict")
