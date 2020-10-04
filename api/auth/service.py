import jwt

from werkzeug.security import generate_password_hash

from api.users.models import User
from api.users.schemas import UserSchema, ResponseUserSchema
from api.auth.validators import validate_unique_email, validate_unique_username
from api.auth.utils import generate_activation_token
from core.exceptions import CustomValidationError
from core.tasks import send_email
from core.settings import USER_ACTIVATION_URL, SECRET_KEY, JWT_ALGORITHM


async def activate_user(token: str):
    """Method for activating user by its email from token
    """
    token = token
    error_text = f"Provided activation token '{token}' is not valid"
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception:
        raise CustomValidationError(field='token', message=error_text)
    obj = await User.get_or_none(email=data['user_email'], is_active=False)
    if not obj:
        raise CustomValidationError(field='token', message=error_text)
    obj.is_active = True
    await obj.save()


async def create_new_user(user: UserSchema):
    """Method for creating new user
    """
    await validate_unique_username(user.username)
    await validate_unique_email(user.email)

    user.password = generate_password_hash(user.dict()['password'], method='sha256')
    user_obj = await User.create(**user.dict(exclude_unset=True))

    token = generate_activation_token(user.email)
    url = f"{USER_ACTIVATION_URL}?token={token}"
    context = {
        'url': url,
        'email': user.email
    }
    template = 'activate_user.html'
    send_email.delay(
        subject="Activate your ChooseOne account",
        template=template,
        recipients=[user.email],
        context=context
    )

    return await ResponseUserSchema.from_tortoise_orm(user_obj)
