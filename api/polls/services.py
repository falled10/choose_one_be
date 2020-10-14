from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from slugify import slugify

from api.polls.schemas import CreatePollSchema, ResponsePollSchema, PatchUpdatePollSchema
from api.polls.models import Poll
from api.polls.validators import validate_unique_title
from api.users.models import User


def create_new_poll(poll: CreatePollSchema, creator: User, db: Session) -> ResponsePollSchema:
    slug = slugify(poll.title)
    poll = Poll(**poll.dict(), creator_id=creator.id, slug=slug)
    db.add(poll)
    db.commit()
    db.refresh(poll)
    return ResponsePollSchema.from_orm(poll)


def update_poll(poll_slug: str, creator: User, update_data: PatchUpdatePollSchema, db: Session) -> ResponsePollSchema:
    poll = db.query(Poll).filter_by(slug=poll_slug).first()
    data = update_data.dict(exclude_unset=True)
    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Poll with id {poll_slug} does not exist")
    if poll.creator_id != creator.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot update this poll")
    if data.get('title'):
        validate_unique_title(poll, data['title'], db)
        data['slug'] = slugify(data['title'])
    db.query(Poll).filter_by(slug=poll_slug).update(data)
    db.refresh(poll)
    db.commit()
    return ResponsePollSchema.from_orm(poll)
