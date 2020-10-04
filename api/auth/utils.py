import jwt

from core.settings import SECRET_KEY, JWT_ALGORITHM


def generate_activation_token(user_email: str) -> str:
    token = jwt.encode({'user_email': user_email, 'type': 'activate'},
                       SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token.decode()
