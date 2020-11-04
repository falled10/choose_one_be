import jwt

from core.settings import SECRET_KEY, JWT_ALGORITHM


def generate_token(user_email: str, token_type) -> str:
    token = jwt.encode({'user_email': user_email, 'type': token_type},
                       SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token.decode()
