from pydantic import EmailStr, validator, constr

from core.database import SessionLocal
from api.users.models import User
from core.schemas import CamelModel


class UserRegistrationSchema(CamelModel):
    email: EmailStr
    username: constr(min_length=2)
    password: constr(min_length=4)

    @validator('email')
    def unique_email(cls, v):
        try:
            db = SessionLocal()
            if db.query(User).filter_by(email=v).first():
                raise ValueError("User with this email already exists!")
        finally:
            db.close()
        return v

    @validator('username')
    def unique_username(cls, v):
        try:
            db = SessionLocal()
            if db.query(User).filter_by(username=v).first():
                raise ValueError("User with this username already exists!")
        finally:
            db.close()
        return v


class UserSchema(CamelModel):
    id: int
    email: EmailStr
    username: str

    class Config:
        orm_mode = True
