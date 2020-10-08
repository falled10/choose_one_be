from fastapi import APIRouter, Depends

from api.polls.schemas import ResponsePollSchema, CreatePollSchema, PatchUpdatePollSchema
from api.polls.services import create_new_poll, update_poll
from api.auth.dependencies import jwt_required
from api.users.models import User


router = APIRouter()


@router.post("", response_model=ResponsePollSchema)
async def create_new_poll_route(poll: CreatePollSchema, user: User = Depends(jwt_required)):
    """Create new poll
    """
    return await create_new_poll(poll, user)


@router.patch("/{poll_id}", response_model=ResponsePollSchema)
async def update_poll_route(poll_id: int, poll: PatchUpdatePollSchema, user: User = Depends(jwt_required)):
    """Update your poll
    """
    return await update_poll(poll_id, user, poll)

