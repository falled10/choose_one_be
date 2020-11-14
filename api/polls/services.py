from typing import List

import httpx

from fastapi.responses import JSONResponse, Response
from sqlalchemy import text
from sqlalchemy.orm import Session, Query
from slugify import slugify
from paginate_sqlalchemy import SqlalchemyOrmPage

from api.polls.schemas import CreatePollSchema, PatchUpdatePollSchema, CreateOptionSchema, OptionUpdateSchema, \
    SelectOptionSchema
from api.polls.models import Poll, Option
from api.polls.validators import validate_unique_title, validate_is_owner, validate_existed_poll, \
    validate_existed_option, validate_places_number
from api.users.models import User
from core.settings import MAX_PLACES_NUMBER, MIN_PLACES_NUMBER, STATISTICS_SERVICE_URL


def get_list_of_all_polls(db: Session, path: str, page_size: int, page: int) -> dict:
    query = db.query(Poll).order_by(text('-id'))
    return get_list_of_polls(path, page_size, page, query)


def get_list_of_my_polls(user: User, db: Session, path: str, page_size: int, page: int) -> dict:
    query = db.query(Poll).filter_by(creator=user).order_by(text('-id'))
    return get_list_of_polls(path, page_size, page, query)


def get_list_of_polls(path: str, page_size: int, page: int, query: Query) -> dict:
    """Returns paginated list of polls
    """
    path = f"{path}?page_size={page_size}&page="
    page = SqlalchemyOrmPage(query, page=page, items_per_page=page_size)
    next_page = page.next_page
    previous_page = page.previous_page
    return {
        'next_page': path + str(next_page) if next_page else None,
        'previous_page': path + str(previous_page) if previous_page else None,
        'results': page.items,
        'count': page.item_count
    }


def get_list_of_searched_polls(path: str, page_size: int, page: int, query: str) -> dict:
    """Returns paginated list of searched polls
    """
    result, total = Poll.search(query, page, page_size)
    path = f"{path}?page_size={page_size}&page="
    return {
        'next_page': path + str(page + 1) if total > page * page_size else None,
        'previous_page': path + str(page - 1) if page > 1 else None,
        'results': result.all(),
        'count': total
    }


def get_single_poll(poll_slug: str, db: Session) -> Poll:
    return validate_existed_poll(db, poll_slug)


def create_new_poll(poll: CreatePollSchema, creator: User, db: Session) -> Poll:
    slug = slugify(poll.title)
    poll = Poll(**poll.dict(), creator_id=creator.id, slug=slug)
    db.add(poll)
    db.commit()
    db.refresh(poll)
    return poll


def update_poll(poll_slug: str, creator: User, update_data: PatchUpdatePollSchema, db: Session) -> Poll:
    poll = validate_existed_poll(db, poll_slug)
    validate_is_owner(poll, creator)
    data = update_data.dict(exclude_unset=True)
    if data.get('title'):
        validate_unique_title(poll, data['title'], db)
        data['slug'] = slugify(data['title'])
    db.query(Poll).filter_by(slug=poll_slug).update(data)
    db.refresh(poll)
    db.commit()
    return poll


def delete_poll(poll_slug: str, creator: User, db: Session):
    poll = validate_existed_poll(db, poll_slug)
    validate_is_owner(poll, creator)
    db.query(Poll).filter_by(id=poll.id).delete()
    db.commit()


def create_option(poll_slug: str, creator: User, option: CreateOptionSchema, db: Session) -> Option:
    poll = validate_existed_poll(db, poll_slug)
    validate_is_owner(poll, creator)
    option = Option(**option.dict(), poll=poll)
    db.add(option)
    db.commit()
    db.refresh(option)
    return option


async def delete_option(poll_slug: str, option_id: int, db: Session, creator: User):
    poll = validate_existed_poll(db, poll_slug)
    validate_is_owner(poll, creator)
    option = validate_existed_option(db, option_id, poll)
    db.query(Option).filter_by(id=option.id).delete()
    db.commit()
    async with httpx.AsyncClient() as client:
        await client.delete(f"{STATISTICS_SERVICE_URL}/api/statistics/{option_id}")


def update_option(data: OptionUpdateSchema, poll_slug: str, option_id: int, db: Session, creator: User) -> Option:
    poll = validate_existed_poll(db, poll_slug)
    validate_is_owner(poll, creator)
    option = validate_existed_option(db, option_id, poll)
    db.query(Option).filter_by(poll=poll, id=option.id).update(data.dict(exclude_unset=True))
    db.commit()
    db.refresh(option)
    return option


def list_of_options(poll_slug: str, db: Session, places_number: int = MAX_PLACES_NUMBER):
    poll = validate_existed_poll(db, poll_slug)
    return list(db.query(Option).filter_by(poll=poll).order_by(text('-id')).limit(places_number))


def get_places_from(from_num: int):
    """Returns sequence of places from `from_num` to `MIN_PLACES_NUMBER`

    Example:
        `from_num` = 64
        result will be [64, 32, 16, 8]
    """
    result = []
    place = from_num
    while place >= MIN_PLACES_NUMBER:
        result.append(place)
        place //= 2
    return result


def poll_places_number(poll_slug: str, db: Session):
    poll = validate_existed_poll(db, poll_slug)
    places_number = db.query(Option).filter_by(poll=poll).count()
    validate_places_number(places_number)
    places_number = places_number if places_number % 2 == 0 else places_number - 1
    max_places = places_number if places_number < MAX_PLACES_NUMBER else MAX_PLACES_NUMBER
    return get_places_from(max_places)


async def send_selected_options_to_statistics(options: List[SelectOptionSchema],
                                              poll_slug: str, db:Session):
    poll = validate_existed_poll(db, poll_slug)
    data = [{**option.dict(), 'poll_id': poll.id} for option in options]
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{STATISTICS_SERVICE_URL}/api/statistics", json={'data': data},
                                 headers={'Content-Type': 'application/json'})
        if resp.status_code == 400:
            return JSONResponse(status_code=resp.status_code, content=resp.json())
        return Response(status_code=204)

