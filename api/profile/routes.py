from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from api.auth.dependencies import jwt_required, get_db
from api.profile.schemas import ForgetPasswordSchema, ResetPasswordSchema
from api.profile.validators import validate_forget_password_token
from api.users.models import User
from api.users.schemas import UserSchema


router = APIRouter()


@router.get("", response_model=UserSchema)
async def current_profile_route(user: User = Depends(jwt_required)):
    return user


@router.post('/password/forget', status_code=status.HTTP_204_NO_CONTENT)
async def forget_password_route(forget_password: ForgetPasswordSchema):
    """Sends password reset notification to user email.
    """
    forget_password.send_by_email(forget_password.email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/password/reset', status_code=status.HTTP_204_NO_CONTENT)
async def reset_password_route(reset_password: ResetPasswordSchema,
                               db: Session = Depends(get_db)):
    """Reset user password
    User should send new password and token that he gets from forget password link
    """
    user = validate_forget_password_token(reset_password.token, db)
    reset_password.change_password(user, reset_password.new_password, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
