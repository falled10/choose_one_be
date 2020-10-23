from fastapi import APIRouter, Depends

from api.auth.dependencies import jwt_required
from api.users.models import User
from api.users.schemas import UserSchema


router = APIRouter()


@router.get("", response_model=UserSchema)
async def current_profile_route(user: User = Depends(jwt_required)):
    return user
