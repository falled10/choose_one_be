from typing import Optional
from typing_extensions import Literal
from pydantic import validator

from api.polls.models import Poll
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
    places_number: int

    class Config:
        orm_mode = True


class PatchUpdatePollSchema(CreatePollSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    media_type: Optional[str] = None
