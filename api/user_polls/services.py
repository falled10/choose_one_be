import httpx

from sqlalchemy.orm import Session

from api.user_polls.models import UserPoll, UserOption
from api.user_polls.schemas import UserPollSchema
from api.users.models import User
from core.settings import STATISTICS_SERVICE_URL


async def create_user_poll(data: UserPollSchema, user: User, db: Session) -> UserPoll:
    transaction = db.begin(subtransactions=True)
    try:
        user_poll = UserPoll(user=user, poll_id=data.poll_id)
        db.add(user_poll)
        db.commit()
        db.refresh(user_poll)
        objects = []
        options_to_statistics = []
        for i, option in enumerate(data.options, 1):
            objects.append(dict(option_id=option.option_id,
                                place_number=i,
                                poll=user_poll))
            if i == 1:
                options_to_statistics.append({
                    'option_id': option.option_id,
                    'poll_id': data.poll_id,
                    'event_type': 'WON'
                })
            options_to_statistics.append({
                'option_id': option.option_id,
                'poll_id': data.poll_id,
                'event_type': 'TOOK_PART_IN_POLL'
            })
        db.bulk_insert_mappings(UserOption, objects)
        db.commit()
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{STATISTICS_SERVICE_URL}/api/statistics",
                                     json={'data': options_to_statistics},
                                     headers={'Content-Type': 'application/json'})
        return resp.json()
    except Exception:
        transaction.rollback()
