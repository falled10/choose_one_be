from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import EmailStr, Field

from api.users.models import User
from core.schemas import CamelModel


BaseResponseUserSchema = pydantic_model_creator(User, name="ResponseUser", exclude=('password',))
BaseUserSchema = pydantic_model_creator(User, name="User", exclude_readonly=True)


class UserSchema(BaseUserSchema, CamelModel):
    email: EmailStr = Field(exclusiveMaximum=255)


class ResponseUserSchema(BaseResponseUserSchema, CamelModel):
    email: EmailStr = Field(exclusiveMaximum=255)
