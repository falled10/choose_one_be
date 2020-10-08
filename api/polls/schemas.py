from tortoise.contrib.pydantic import pydantic_model_creator

from api.polls.models import Poll


BasePollSchema = pydantic_model_creator(Poll, name="PollSchema", exclude_readonly=True)


class ResponsePollSchema(BasePollSchema):
    id: int
    slug: str
