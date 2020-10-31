from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from api.auth.dependencies import jwt_required, get_db
from api.user_polls.schemas import ResponseUserPollSchema, UserPollSchema
from api.user_polls.services import create_user_poll
from api.users.models import User


router = APIRouter()


@router.post('', response_model=ResponseUserPollSchema, status_code=status.HTTP_201_CREATED)
def create_user_poll_route(user_poll: UserPollSchema, user: User = Depends(jwt_required),
                           db: Session = Depends(get_db)):
    """Create result poll for current user
    """
    return create_user_poll(user_poll, user, db)
