from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session, joinedload

from api.polls.schemas import CreatePollSchema, ResponsePollSchema, PatchUpdatePollSchema
from api.polls.models import Poll
from api.users.models import User


def create_new_poll(poll: CreatePollSchema, creator: User, db: Session) -> ResponsePollSchema:
    poll = Poll(**poll.dict(), creator=creator.id)
    db.add(poll)
    db.commit()
    db.refresh(poll)
    return ResponsePollSchema.from_orm(poll)


def update_poll(poll_id: int, creator: User, update_data: PatchUpdatePollSchema, db: Session) -> ResponsePollSchema:
    poll = db.query(Poll).get(poll_id).options(joinedload('creator'))
    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Poll with id {poll_id} does not exist")
    if poll.creator != creator.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot update this poll")
    poll = poll.update(update_data.dict(exclude_unset=True))
    db.commit()
    db.refresh(poll)
    return ResponsePollSchema.from_orm(poll)
