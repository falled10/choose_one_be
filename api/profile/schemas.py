from pydantic import EmailStr, validator

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
