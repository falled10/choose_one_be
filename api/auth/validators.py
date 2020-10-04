from api.users.models import User
from core.exceptions import CustomValidationError


async def validate_unique_email(email: str):
    obj = await User.get_or_none(email=email)
    if obj:
        raise CustomValidationError(field='email', message="User with that email already exists!")


async def validate_unique_username(username: str):
    obj = await User.get_or_none(username=username)
    if obj:
        raise CustomValidationError(field='username', message="User with that username already exists!")
