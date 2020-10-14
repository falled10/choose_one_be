from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.polls.schemas import ResponsePollSchema, CreatePollSchema, PatchUpdatePollSchema
from api.polls.services import create_new_poll, update_poll
from api.auth.dependencies import jwt_required, get_db
from api.users.models import User


router = APIRouter()


@router.post("", response_model=ResponsePollSchema, status_code=status.HTTP_201_CREATED)
async def create_new_poll_route(poll: CreatePollSchema, user: User = Depends(jwt_required),
                                db: Session = Depends(get_db)):
    """Create new poll
    """
    return create_new_poll(poll, user, db)


@router.patch("/{poll_slug}", response_model=ResponsePollSchema)
async def update_poll_route(poll_slug: str, poll: PatchUpdatePollSchema, user: User = Depends(jwt_required),
                            db: Session = Depends(get_db)):
    """Update your poll
    """
    return update_poll(poll_slug, user, poll, db)
