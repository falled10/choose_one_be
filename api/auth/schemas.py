from pydantic import EmailStr

from core.schemas import CamelModel


class ActivateUserSchema(CamelModel):
    token: str


class UserLoginSchema(CamelModel):
    email: EmailStr
    password: str


class TokensSchema(CamelModel):
    access: str
    refresh: str


class RefreshTokenSchema(CamelModel):
    refresh: str
