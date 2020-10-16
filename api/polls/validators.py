from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from api.polls.models import Poll
from api.users.models import User
from core.exceptions import CustomValidationError


def validate_unique_title(poll: Poll, title: str, db: Session):
    obj = db.query(Poll).filter_by(title=title).first()
    if obj and obj != poll:
        raise CustomValidationError(field="title", message="Poll with this title already exists")


def validate_is_owner(poll: Poll, creator: User):
    if poll.creator_id != creator.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot update this poll")


def validate_existed_poll(db: Session, poll_slug):
    poll = db.query(Poll).filter_by(slug=poll_slug).first()
    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Poll with id {poll_slug} does not exist")
    return poll
