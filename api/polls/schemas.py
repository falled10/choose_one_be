from typing import Optional
from pydantic import Field

from api.polls.choices import MediaType
from core.schemas import CamelModel


class CreatePollSchema(CamelModel):
    title: str
    description: str
    media_type: MediaType = Field(default=MediaType.IMAGE)


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
