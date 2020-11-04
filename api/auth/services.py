import jwt
from sqlalchemy.orm import Session

from werkzeug.security import generate_password_hash

from api.users.models import User
from api.users.schemas import UserSchema, UserRegistrationSchema
from api.auth.utils import generate_token
from core.exceptions import CustomValidationError
from core.tasks import send_email
from core.settings import USER_ACTIVATION_URL, SECRET_KEY, JWT_ALGORITHM


def activate_user(token: str, db: Session):
    """Method for activating user by its email from token
    """
    token = token
    error_text = f"Provided activation token '{token}' is not valid"
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if data['type'] != 'activate':
            raise
    except Exception:
        raise CustomValidationError(field='token', message=error_text)
    obj = db.query(User).filter_by(email=data['user_email'], is_active=False).first()
    if not obj:
        raise CustomValidationError(field='token', message=error_text)
    obj.is_active = True
    db.commit()


def create_new_user(user: UserRegistrationSchema, db: Session):
    """Method for creating new user
    """

    user.password = generate_password_hash(user.dict()['password'], method='sha256')
    user_obj = User(**user.dict(exclude_unset=True))
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    token = generate_token(user.email, 'activate')
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

    return UserSchema.from_orm(user_obj)
