from typing import List

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from api.auth.dependencies import jwt_required, get_db
from api.user_polls.schemas import CalculatedOptionSchema, UserPollSchema
from api.user_polls.services import create_user_poll, send_statistics_to_service
from api.users.models import User


router = APIRouter()


@router.post('', response_model=List[CalculatedOptionSchema], status_code=status.HTTP_201_CREATED)
async def create_user_poll_route(user_poll: UserPollSchema, user: User = Depends(jwt_required),
                                 db: Session = Depends(get_db)):
    """Create result poll for current user
    """
    return await create_user_poll(user_poll, user, db)


@router.post('/anonymous', response_model=List[CalculatedOptionSchema], status_code=status.HTTP_201_CREATED)
async def create_user_poll_as_anon_route(user_poll: UserPollSchema):
    options = []
    for i, option in enumerate(user_poll.options, 1):
        if i == 1:
            options.append({
                'option_id': option.option_id,
                'poll_id': user_poll.poll_id,
                'event_type': 'WON'
            })
        options.append({
            'option_id': option.option_id,
            'poll_id': user_poll.poll_id,
            'event_type': 'TOOK_PART_IN_POLL'
        })
    return await send_statistics_to_service(options)
