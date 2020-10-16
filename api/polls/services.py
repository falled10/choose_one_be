from sqlalchemy.orm import Session
from slugify import slugify

from api.polls.schemas import CreatePollSchema, ResponsePollSchema, PatchUpdatePollSchema
from api.polls.models import Poll
from api.polls.validators import validate_unique_title, validate_is_owner, validate_existed_poll
from api.users.models import User


def create_new_poll(poll: CreatePollSchema, creator: User, db: Session) -> ResponsePollSchema:
    slug = slugify(poll.title)
    poll = Poll(**poll.dict(), creator_id=creator.id, slug=slug)
    db.add(poll)
    db.commit()
    db.refresh(poll)
    return ResponsePollSchema.from_orm(poll)


def update_poll(poll_slug: str, creator: User, update_data: PatchUpdatePollSchema, db: Session) -> ResponsePollSchema:
    poll = validate_existed_poll(db, poll_slug)
    validate_is_owner(poll, creator)
    data = update_data.dict(exclude_unset=True)
    if data.get('title'):
        validate_unique_title(poll, data['title'], db)
        data['slug'] = slugify(data['title'])
    db.query(Poll).filter_by(slug=poll_slug).update(data)
    db.refresh(poll)
    db.commit()
    return ResponsePollSchema.from_orm(poll)


def delete_poll(poll_slug: str, creator: User, db: Session):
    poll = validate_existed_poll(db, poll_slug)
    validate_is_owner(poll, creator)
    db.query(Poll).filter_by(id=poll.id).delete()
    db.commit()
