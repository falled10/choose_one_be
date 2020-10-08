from fastapi import APIRouter, Depends

from api.polls.schemas import ResponsePollSchema, BasePollSchema
from api.polls.services import create_new_poll
from api.auth.dependencies import jwt_required
from api.users.models import User


router = APIRouter()


@router.post("", response_model=ResponsePollSchema)
async def create_new_poll_route(poll: BasePollSchema, user: User = Depends(jwt_required)):
    """Create new poll
    """
    return await create_new_poll(poll, user)
