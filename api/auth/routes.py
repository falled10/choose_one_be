from fastapi import APIRouter, status, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from api.auth.authorization import authorize_user, refresh_tokens
from api.users.schemas import UserSchema, UserRegistrationSchema
from api.auth.service import create_new_user, activate_user
from api.auth.dependencies import get_db
from api.auth.schemas import ActivateUserSchema, TokensSchema, UserLoginSchema, RefreshTokenSchema

router = APIRouter()


@router.post('/register', response_model=UserSchema, status_code=201)
async def register_route(user: UserRegistrationSchema, db: Session = Depends(get_db)):
    """Create new user
    """
    return create_new_user(user, db)


@router.post('/activate', status_code=204)
async def activate_user_route(token: ActivateUserSchema, db: Session = Depends(get_db)):
    """Activate non active existed user
    """
    activate_user(token.token, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/login', response_model=TokensSchema)
async def login(user: UserLoginSchema, db: Session = Depends(get_db)):
    """Authorize new user and get access and refresh tokens
    """
    return authorize_user(user, db)


@router.post('/refresh', response_model=TokensSchema)
async def refresh_token_route(token: RefreshTokenSchema, db: Session = Depends(get_db)):
    """Refresh old tokens by passing `refresh` token
    and get new ones
    """
    return refresh_tokens(token.refresh, db)
