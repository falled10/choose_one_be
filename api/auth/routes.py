from fastapi import APIRouter, status
from fastapi.responses import Response

from api.auth.authorization import authorize_user, refresh_tokens
from api.users.schemas import UserSchema, ResponseUserSchema
from api.auth.service import create_new_user, activate_user
from api.auth.schemas import ActivateUserSchema, TokensSchema, UserLoginSchema, RefreshTokenSchema

router = APIRouter()


@router.post('/register', response_model=ResponseUserSchema, status_code=201)
async def register_route(user: UserSchema):
    """Create new user
    """
    return await create_new_user(user)


@router.post('/activate', status_code=204)
async def activate_user_route(token: ActivateUserSchema):
    """Activate non active existed user
    """
    await activate_user(token.token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/login', response_model=TokensSchema)
async def login(user: UserLoginSchema):
    """Authorize new user and get access and refresh tokens
    """
    return await authorize_user(user)


@router.post('/refresh', response_model=TokensSchema)
async def refresh_token_route(token: RefreshTokenSchema):
    """Refresh old tokens by passing `refresh` token
    and get new ones
    """
    return await refresh_tokens(token.refresh)
