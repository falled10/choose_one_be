from typing import List

from pydantic import validator

from api.polls.models import Poll
from core.database import SessionLocal
from core.schemas import CamelModel


class UserOptionSchema(CamelModel):
    option_id: int


class UserPollSchema(CamelModel):
    poll_id: int
    options: List[UserOptionSchema]

    @validator("poll_id")
    def check_existed_poll(cls, v):
        try:
            db = SessionLocal()
            if not db.query(Poll).get(v):
                raise ValueError("Poll does not exists with this id")
        finally:
            db.close()
        return v

    @validator('options')
    def check_poll_options(cls, v, values, **kwargs):
        try:
            db = SessionLocal()
            if values.get('poll_id'):
                poll = db.query(Poll).get(values.get('poll_id'))
                options = poll.options
                options_ids = [option.id for option in options]
                for option in v:
                    if option.option_id not in options_ids:
                        raise ValueError("Option with this id does not exists")
        finally:
            db.close()
        return v


class CalculatedOptionSchema(CamelModel):
    option_id: int
    selected_percentage: int
    win_percentage: int
