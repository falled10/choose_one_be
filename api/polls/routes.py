from typing import Optional, List

from fastapi import APIRouter, Depends, status, Request
from fastapi.params import Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from api.polls.schemas import ResponsePollSchema, CreatePollSchema, PatchUpdatePollSchema, ListPollResponseSchema, \
    OptionSchema, CreateOptionSchema, OptionUpdateSchema
from api.polls.services import create_new_poll, update_poll, delete_poll, get_single_poll, \
    get_list_of_all_polls, get_list_of_my_polls, create_option, delete_option, update_option, list_of_options, \
    poll_places_number, get_list_of_searched_polls
from api.auth.dependencies import jwt_required, get_db
from api.users.models import User
from core.settings import MAX_PLACES_NUMBER

router = APIRouter()


@router.get("/my-polls", response_model=ListPollResponseSchema)
async def list_of_my_polls_route(request: Request, page: int = 1,
                                 page_size: Optional[int] = Query(20, gt=0), db: Session = Depends(get_db),
                                 user: User = Depends(jwt_required)):
    return get_list_of_my_polls(user, db, request.url.path, page_size, page)


@router.get("/search/{query}", response_model=ListPollResponseSchema)
async def search_polls_route(query: str, request: Request, page: int = 1,
                             page_size: Optional[int] = Query(20, gt=0)):
    return get_list_of_searched_polls(request.url.path, page_size, page, query)


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
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{poll_slug}", response_model=ResponsePollSchema)
async def get_single_poll_endpoint(poll_slug: str, db: Session = Depends(get_db)):
    """Get single poll"""
    return get_single_poll(poll_slug, db)


@router.get("", response_model=ListPollResponseSchema)
async def list_of_poll_route(request: Request, page: int = 1,
                             page_size: Optional[int] = Query(20, gt=0), db: Session = Depends(get_db)):
    """Get paginated list of polls
    """
    return get_list_of_all_polls(db, request.url.path, page_size, page)


@router.get('/{poll_slug}/places-numbers', response_model=List[int])
async def poll_places_number_route(poll_slug: str, db: Session = Depends(get_db)):
    return poll_places_number(poll_slug, db)


@router.post("/{poll_slug}/options", response_model=OptionSchema, status_code=status.HTTP_201_CREATED)
async def create_new_option_route(new_option: CreateOptionSchema, poll_slug: str, user: User = Depends(jwt_required),
                                  db: Session = Depends(get_db)):
    return create_option(poll_slug, user, new_option, db)


@router.delete("/{poll_slug}/options/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existed_poll_route(poll_slug: str, option_id: int, user: User = Depends(jwt_required),
                                    db: Session = Depends(get_db)):
    delete_option(poll_slug, option_id, db, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{poll_slug}/options/{option_id}", response_model=OptionSchema, status_code=status.HTTP_200_OK)
async def update_option_route(option_data: OptionUpdateSchema, poll_slug: str, option_id: int,
                              user: User = Depends(jwt_required),
                              db: Session = Depends(get_db)):
    return update_option(option_data, poll_slug, option_id, db, user)


@router.get('/{poll_slug}/options', response_model=List[OptionSchema])
async def list_of_options_route(poll_slug: str, places_number: int = MAX_PLACES_NUMBER, db: Session = Depends(get_db)):
    return list_of_options(poll_slug, db, places_number)
