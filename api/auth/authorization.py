import jwt
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from werkzeug.security import check_password_hash
from sqlalchemy.orm import Session

from api.auth.schemas import UserLoginSchema
from api.users.models import User
from core.settings import SECRET_KEY, JWT_ALGORITHM, \
    JWT_PREFIX, JWT_TOKEN_LIFE_TIME, JWT_REFRESH_TOKEN_LIFE_TIME
from core.database import SessionLocal


INVALID_TOKEN_ERROR = 'Invalid token.'


def get_current_user(data: dict) -> User:
    """Return current logged in user
    """
    try:
        db = SessionLocal()
        user = db.query(User).get(data['user_id'])
        if not user or data['type'] == 'refresh':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_TOKEN_ERROR)
        return user
    finally:
        db.close()


def _decode_token(token: str) -> dict:
    """Decode token and return data from it
    """
    if not token:
        raise HTTPException(status_code=401, detail=INVALID_TOKEN_ERROR)
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return data
    except Exception:
        raise HTTPException(status_code=401, detail=INVALID_TOKEN_ERROR)


def get_data_form_token(token_string: str) -> dict:
    """Select prefix and token from `token_string`

    :param token_string: string token prefix and token itself
    """
    try:
        prefix, token = token_string.split(' ')
        if prefix != JWT_PREFIX:
            raise HTTPException(status_code=401, detail="Invalid JWT prefix")
        return _decode_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail=INVALID_TOKEN_ERROR)


def _generate_token(user: User, token_type: str, time: int) -> str:
    return jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=time),
        'type': token_type
    }, SECRET_KEY, algorithm=JWT_ALGORITHM).decode()


def get_access_token(user: User) -> str:
    """Return access token for `user`
    """
    return _generate_token(user, 'access', JWT_TOKEN_LIFE_TIME)


def get_refresh_token(user: User) -> str:
    """Return refresh token for `user`
    """
    return _generate_token(user, 'refresh', JWT_REFRESH_TOKEN_LIFE_TIME)


def refresh_tokens(refresh_token: str, db: Session) -> dict:
    """Refresh all tokens for user
    """
    data = _decode_token(refresh_token)
    if data.get('type') == 'refresh':
        user = db.query(User).filter_by(id=data['user_id'], is_active=True).first()
        if user:
            return {
                'access': get_access_token(user),
                'refresh': get_refresh_token(user)
            }
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_TOKEN_ERROR)


def authorize_user(credentials: UserLoginSchema, db: Session) -> dict:
    """Use this method to authorize user and return tokens
    """
    error_message = "User with this credentials doesn't exists."
    user = db.query(User).filter_by(email=credentials.email, is_active=True).first()
    if not user or not check_password_hash(user.password, credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_message)
    return {
        'access': get_access_token(user),
        'refresh': get_refresh_token(user)
    }
