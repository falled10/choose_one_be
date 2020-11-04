from pydantic import EmailStr, validator, root_validator
from pydantic.types import constr
from werkzeug.security import generate_password_hash

from api.auth.utils import generate_token
from api.users.models import User
from core.database import SessionLocal
from core.schemas import CamelModel
from core.tasks import send_email
from core.settings import PASSWORD_RESET_URL


class ForgetPasswordSchema(CamelModel):
    email: EmailStr

    @validator('email')
    def unique_email(cls, v):
        try:
            db = SessionLocal()
            if not db.query(User).filter_by(email=v).first():
                raise ValueError("User with this email does not exist.")
        finally:
            db.close()
        return v

    @staticmethod
    def send_by_email(email):
        try:
            db = SessionLocal()
            user = db.query(User).filter_by(email=email).first()
            token = generate_token(user.email, 'forget_password')
            url = f"{PASSWORD_RESET_URL}?token={token}"
            send_email.delay(
                subject="ChooseOne Password Restoring",
                template='notifications/password_forget.html',
                recipients=[user.email],
                context={'url': url, 'email': user.email}
            )
        finally:
            db.close()


class PasswordSchema(CamelModel):
    """Base schema for password changing
    """
    new_password: constr(min_length=4)
    confirmed_password: constr(min_length=4)

    @root_validator
    def validate_passwords_match(cls, values):
        new_password = values['new_password']
        confirmed_password = values['confirmed_password']
        if new_password != confirmed_password:
            raise ValueError("The two password fields didn't match.")
        return values


class ResetPasswordSchema(PasswordSchema):
    token: str

    @staticmethod
    def change_password(user, new_password, db):
        user.password = generate_password_hash(new_password, method='sha256')
        db.commit()
        db.refresh(user)
        return user
