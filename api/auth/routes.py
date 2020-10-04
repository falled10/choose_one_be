from fastapi import APIRouter

from api.users.schemas import UserSchema, ResponseUserSchema
from api.auth.service import create_new_user


router = APIRouter()


@router.post('/register', response_model=ResponseUserSchema)
async def register(user: UserSchema):
    return await create_new_user(user)
