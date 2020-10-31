from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from api.polls.models import Poll, Option
from api.users.models import User
from core.exceptions import CustomValidationError
from core.settings import MIN_PLACES_NUMBER


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
                            detail=f"Poll with slug {poll_slug} does not exist")
    return poll


def validate_existed_option(db: Session, option_id: int, poll: Poll):
    option = db.query(Option).filter_by(id=option_id, poll=poll).first()
    if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Option with id {option_id} does not exist")
    return option


def validate_places_number(places_number: int):
    if places_number < MIN_PLACES_NUMBER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Poll should contain more options")
