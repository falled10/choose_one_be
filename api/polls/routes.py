from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.polls.schemas import ResponsePollSchema, CreatePollSchema, PatchUpdatePollSchema
from api.polls.services import create_new_poll, update_poll, delete_poll, get_single_poll
from api.auth.dependencies import jwt_required, get_db
from api.users.models import User


router = APIRouter()


@router.post("", response_model=ResponsePollSchema, status_code=status.HTTP_201_CREATED)
async def create_new_poll_route(poll: CreatePollSchema, user: User = Depends(jwt_required),
                                db: Session = Depends(get_db)):
    """Create new poll
    """
    return create_new_poll(poll, user, db)


@router.patch("/{poll_slug}", response_model=ResponsePollSchema)
async def update_poll_route(poll_slug: str, poll: PatchUpdatePollSchema, user: User = Depends(jwt_required),
                            db: Session = Depends(get_db)):
    """Update your poll
    """
    return update_poll(poll_slug, user, poll, db)


@router.delete("/{poll_slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_poll_route(poll_slug: str, user: User = Depends(jwt_required), db: Session = Depends(get_db)):
    """Delete Existed poll"""
    delete_poll(poll_slug, user, db)
    return


@router.get("/{poll_slug}", response_model=ResponsePollSchema)
async def get_single_poll_endpoint(poll_slug: str, db: Session = Depends(get_db)):
    """Get single poll"""
    return get_single_poll(poll_slug, db)
