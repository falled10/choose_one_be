import jwt

from api.users.models import User
from core.exceptions import CustomValidationError
from core.settings import SECRET_KEY, JWT_ALGORITHM


def validate_forget_password_token(token: str, db):
    error_text = f"Provided reset token '{token}' is not valid"
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if data['type'] != 'forget_password':
            raise
    except Exception:
        raise CustomValidationError(field='token', message=error_text)
    obj = db.query(User).filter_by(email=data['user_email']).first()
    if not obj:
        raise CustomValidationError(field='token', message=error_text)
    return obj
