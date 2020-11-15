from sqlalchemy.orm import Session

from api.user_polls.models import UserPoll, UserOption
from api.user_polls.schemas import UserPollSchema
from api.users.models import User


def create_user_poll(data: UserPollSchema, user: User, db: Session) -> UserPoll:
    transaction = db.begin(subtransactions=True)
    try:
        user_poll = UserPoll(user=user, poll_id=data.poll_id)
        db.add(user_poll)
        db.commit()
        db.refresh(user_poll)
        objects = []
        for i, option in enumerate(data.options, 1):
            objects.append(UserOption(option_id=option.option_id,
                                      place_number=i,
                                      poll=user_poll))
        db.bulk_save_objects(objects)
        db.commit()
        return user_poll
    except Exception:
        transaction.rollback()
