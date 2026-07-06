from fastapi import APIRouter, Depends
from app.api.v1.auth import _serialize_user, router as auth_router
from app.api.v1.activities import router as activities_router
# from app.api.v1.search import router as search_router  # disabled for lightweight testing
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(activities_router)
# api_router.include_router(search_router)  # disabled for lightweight testing


@api_router.get("/users/me", response_model=UserResponse)
async def get_user_me(current_user: User = Depends(get_current_user)):
    return _serialize_user(current_user)
