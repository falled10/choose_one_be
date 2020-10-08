from api.polls.schemas import BasePollSchema, ResponsePollSchema
from api.polls.models import Poll
from api.users.models import User


async def create_new_poll(poll: BasePollSchema, creator: User) -> ResponsePollSchema:
    print(poll.dict())
    poll = await Poll.create(**poll.dict(), creator=creator)
    return await ResponsePollSchema.from_tortoise_orm(poll)
