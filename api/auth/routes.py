from fastapi import APIRouter

from api.users.schemas import UserSchema, ResponseUserSchema
from api.auth.service import create_new_user, activate_user
from api.auth.schemas import ActivateUserSchema


router = APIRouter()


@router.post('/register', response_model=ResponseUserSchema, status_code=201)
async def register(user: UserSchema):
    return await create_new_user(user)


@router.post('/activate', status_code=204)
async def activate_user_route(token: ActivateUserSchema):
    await activate_user(token.token)
    return
