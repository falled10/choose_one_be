from fastapi import status
from fastapi.exceptions import HTTPException

from api.polls.schemas import CreatePollSchema, ResponsePollSchema, PatchUpdatePollSchema
from api.polls.models import Poll
from api.users.models import User


async def create_new_poll(poll: CreatePollSchema, creator: User) -> ResponsePollSchema:
    poll = await Poll.create(**poll.dict(), creator=creator)
    return await ResponsePollSchema.from_tortoise_orm(poll)


async def update_poll(poll_id: int, creator: User, update_data: PatchUpdatePollSchema) -> ResponsePollSchema:
    poll = await Poll.get_or_none(pk=poll_id).prefetch_related('creator')
    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Poll with id {poll_id} does not exist")
    if poll.creator.id != creator.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot update this poll")
    poll = await poll.update_from_dict(update_data.dict(exclude_unset=True))
    return await ResponsePollSchema.from_tortoise_orm(poll)
