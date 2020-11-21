from typing import Optional, List
from typing_extensions import Literal
from pydantic import validator

from api.polls.models import Poll, Option
from core.database import SessionLocal
from core.schemas import CamelModel


class CreatePollSchema(CamelModel):
    title: str
    description: Optional[str] = ""
    media_type: Literal['Image', 'GIF', 'Video'] = "Image"

    @validator('title')
    def unique_title(cls, v):
        try:
            db = SessionLocal()
            poll = db.query(Poll).filter_by(title=v).first()
            if poll:
                raise ValueError('Poll with this title already exists')
        finally:
            db.close()
        return v


class ResponsePollSchema(CamelModel):
    id: int
    title: str
    description: str
    media_type: str
    slug: str

    class Config:
        orm_mode = True


class PatchUpdatePollSchema(CamelModel):
    title: Optional[str] = None
    description: Optional[str] = None
    media_type: Optional[Literal['Image', 'GIF', 'Video']] = None


class ListPollResponseSchema(CamelModel):
    next_page: Optional[str] = None
    previous_page: Optional[str] = None
    results: List[ResponsePollSchema]
    count: int


class CreateOptionSchema(CamelModel):
    label: str
    media: Optional[str] = None


class OptionSchema(CreateOptionSchema):
    id: int

    class Config:
        orm_mode = True


class OptionUpdateSchema(CamelModel):
    label: Optional[str]
    media: Optional[str]

    @validator('label')
    def non_none_label(cls, v):
        if v is None:
            raise ValueError("Label cannot be None")
        return v


class SelectOptionSchema(CamelModel):
    option_id: int
    event_type: str

    @validator("option_id")
    def check_existed_option(cls, v):
        try:
            db = SessionLocal()
            if not db.query(Option).get(v):
                raise ValueError("Option does not exists with this id")
        finally:
            db.close()
        return v
