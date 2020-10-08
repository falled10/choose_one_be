from typing import Optional
from pydantic import Field

from tortoise.contrib.pydantic import pydantic_model_creator

from api.polls.models import Poll
from api.polls.choices import MediaType
from core.schemas import CamelModel

BasePollSchema = pydantic_model_creator(Poll, name="PollSchema", exclude_readonly=True)


class CreatePollSchema(CamelModel, BasePollSchema):
    media_type: MediaType = Field(default=MediaType.IMAGE)


class ResponsePollSchema(CamelModel, BasePollSchema):
    id: int
    slug: str
    places_number: int


class PatchUpdatePollSchema(CreatePollSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    media_type: Optional[str] = None
