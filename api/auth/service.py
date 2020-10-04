from werkzeug.security import generate_password_hash

from api.users.models import User
from api.users.schemas import UserSchema, ResponseUserSchema
from api.auth.validators import validate_unique_email, validate_unique_username


async def create_new_user(user: UserSchema):
    await validate_unique_username(user.username)
    await validate_unique_email(user.email)
    user.password = generate_password_hash(user.dict()['password'], method='sha256')
    user_obj = await User.create(**user.dict(exclude_unset=True))
    return await ResponseUserSchema.from_tortoise_orm(user_obj)
