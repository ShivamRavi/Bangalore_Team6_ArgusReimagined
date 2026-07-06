from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from datetime import timedelta
import uuid

from app.database import get_db
from app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token, decode_token
)
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.house import House
from app.models.section import Section
from app.schemas.auth import RegisterRequest, TokenResponse, RefreshRequest
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        payload_data = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid JSON body") from exc

    payload = RegisterRequest.model_validate(payload_data)

    # 1. Check if user already exists
    existing_query = select(User).where(User.username == payload.username)
    existing_result = await db.execute(existing_query)
    if existing_result.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )

    explicitly_requested_student_role = bool(payload_data.get("role") == "STUDENT")

    # 2. Resolve house/section for STUDENT accounts or fall back to the first seeded defaults.
    if payload.role == "STUDENT":
        if explicitly_requested_student_role and payload.house_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="house_id is required for STUDENT role")
        if explicitly_requested_student_role and payload.section_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="section_id is required for STUDENT role")

        if payload.house_id is None:
            house_result = await db.execute(select(House).order_by(House.id).limit(1))
            default_house = house_result.scalars().first()
            if default_house is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No houses are available for registration"
                )
            payload.house_id = default_house.id
        else:
            house_query = select(House).where(House.id == payload.house_id)
            house_result = await db.execute(house_query)
            if house_result.scalars().first() is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"House with ID {payload.house_id} does not exist"
                )

        if payload.section_id is None:
            section_result = await db.execute(select(Section).order_by(Section.id).limit(1))
            default_section = section_result.scalars().first()
            if default_section is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No sections are available for registration"
                )
            payload.section_id = default_section.id
        else:
            section_query = select(Section).where(Section.id == payload.section_id)
            section_result = await db.execute(section_query)
            if section_result.scalars().first() is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Section with ID {payload.section_id} does not exist"
                )

    # 3. Create user
    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        house_id=payload.house_id,
        section_id=payload.section_id,
        euros_balance=0,
        lifetime_euros=0,
        current_planet="Mercury",
        current_streak=0
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 4. Generate tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(request.refresh_token)
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id_str is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def _serialize_user(current_user: User) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        house_id=current_user.house_id,
        house_name=current_user.house.name if current_user.house else None,
        section_id=current_user.section_id,
        section_name=current_user.section.name if current_user.section else None,
        euros_balance=current_user.euros_balance,
        lifetime_euros=current_user.lifetime_euros,
        current_planet=current_user.current_planet,
        current_streak=current_user.current_streak,
        last_active_at=current_user.last_active_at,
        created_at=current_user.created_at,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return _serialize_user(current_user)


@router.get("/users/me", response_model=UserResponse)
async def get_user_me(current_user: User = Depends(get_current_user)):
    return _serialize_user(current_user)


@router.post("/otp-login")
async def otp_login():
    """Stub OTP Login returning 501 Not Implemented."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OTP Login is not implemented yet. Please use username/password login."
    )
