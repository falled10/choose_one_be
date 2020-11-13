from typing import List
from datetime import datetime

from pydantic import validator

from api.polls.models import Poll, Option
from core.database import SessionLocal
from core.schemas import CamelModel


class UserOptionSchema(CamelModel):
    option_id: int
    place_number: int


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


class ResponseUserPollSchema(CamelModel):
    id: int
    poll_id: int
    created_at: datetime

    class Config:
        orm_mode = True
