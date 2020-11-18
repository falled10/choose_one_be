import httpx

from unittest.mock import MagicMock
import pytest
from fastapi.exceptions import HTTPException
from slugify import slugify
from sqlalchemy import text

from api.polls.services import create_new_poll, send_selected_options_to_statistics, update_poll,\
    delete_poll, get_single_poll, get_list_of_polls, get_list_of_all_polls, get_list_of_my_polls, \
    create_option, get_places_from
from api.polls.validators import validate_unique_title, validate_is_owner, validate_existed_poll
from api.polls.models import Poll
from api.polls.schemas import PatchUpdatePollSchema, CreatePollSchema, CreateOptionSchema, SelectOptionSchema
from core.exceptions import CustomValidationError


def test_create_new_poll(active_user, db):
    poll = CreatePollSchema(title="new test poll", description="Something about test poll")
    new_poll = create_new_poll(poll, active_user, db)
    assert new_poll.title == poll.title
    assert new_poll.description == poll.description
    assert db.query(Poll).get(new_poll.id)
    assert new_poll.slug == slugify(new_poll.title)


def test_update_existed_poll(active_user, db, poll):
    old_title = poll.title
    data = PatchUpdatePollSchema(title="updated title")
    updated_poll = update_poll(poll.slug, active_user, data, db)
    assert updated_poll.description == poll.description
    assert updated_poll.title != old_title
    assert updated_poll.title == data.title
    assert updated_poll.slug == slugify(data.title)
    new_poll = db.query(Poll).get(poll.id)
    assert new_poll.title == data.title


def test_update_existed_poll_not_title(active_user, db, poll):
    old_title = poll.title
    data = PatchUpdatePollSchema(description="updated description")
    updated_poll = update_poll(poll.slug, active_user, data, db)
    assert updated_poll.description == poll.description
    assert updated_poll.title == old_title


def test_update_non_existed_poll(active_user, db):
    data = PatchUpdatePollSchema(title="updated title")
    with pytest.raises(HTTPException):
        update_poll('asdfasdf', active_user, data, db)


def test_update_other_users_poll(user, db, poll):
    data = PatchUpdatePollSchema(title="updated title")
    with pytest.raises(HTTPException):
        update_poll(poll.slug, user, data, db)


def test_validate_unique_title(db, user, poll):
    data = CreatePollSchema(title='some another title', description='some another description')
    another_poll = create_new_poll(data, user, db)
    with pytest.raises(CustomValidationError):
        validate_unique_title(poll, another_poll.title, db)


def test_delete_existed_poll(db, active_user, poll):
    delete_poll(poll.slug, active_user, db)
    assert not db.query(Poll).filter_by(id=poll.id).first()


def test_delete_not_existed_poll(db, active_user):
    with pytest.raises(HTTPException):
        delete_poll('asdfasdfasdf', active_user, db)


def test_delete_poll_from_another_user(db, user, poll):
    with pytest.raises(HTTPException):
        delete_poll(poll.slug, user, db)


def test_validate_is_owner(poll, user):
    with pytest.raises(HTTPException):
        validate_is_owner(poll, user)


def test_validate_existed_poll(db, poll):
    existed_poll = validate_existed_poll(db, poll.slug)
    assert existed_poll.id == poll.id
    assert existed_poll.slug == poll.slug


def test_validate_not_existed_poll(db):
    with pytest.raises(HTTPException):
        validate_existed_poll(db, 'asdfljadsjfk')


def test_get_single_poll(db, poll):
    existed_poll = get_single_poll(poll.slug, db)
    assert existed_poll.slug == poll.slug
    assert existed_poll.id == poll.id


def test_get_not_existed_poll(db):
    with pytest.raises(HTTPException):
        get_single_poll('asdjfjasdfl', db)


def test_get_list_of_polls(poll, active_user, db):
    title = 'some other poll'
    other_poll = Poll(title=title, description="Something about test poll", slug=slugify(title),
                      creator=active_user)
    db.add(other_poll)
    db.commit()
    db.refresh(other_poll)
    query = db.query(Poll).order_by(text('-id'))
    data = get_list_of_polls('/api/polls', 2, 1, query)
    assert data['count'] == 2
    assert not data['next_page']
    assert data['results'][0].id == other_poll.id
    assert data['results'][1].id == poll.id


def test_get_list_of_polls_has_next_page(poll, active_user, db):
    title = 'some other poll'
    other_poll = Poll(title=title, description="Something about test poll", slug=slugify(title),
                      creator=active_user)
    db.add(other_poll)
    db.commit()
    query = db.query(Poll).order_by(text('-id'))
    data = get_list_of_polls('/api/polls', 1, 1, query)
    assert data['count'] == 2
    assert data['next_page']


def test_get_list_of_all_polls(poll, active_user, db):
    title = 'some other poll'
    other_poll = Poll(title=title, description="Something about test poll", slug=slugify(title),
                      creator=active_user)
    db.add(other_poll)
    db.commit()
    data = get_list_of_all_polls(db, '/api/polls', 2, 1)
    assert data['count'] == 2
    assert data['results'][0].id == other_poll.id


def test_get_list_of_my_polls(poll, user, active_user, db):
    title = 'some other poll'
    other_poll = Poll(title=title, description="Something about test poll", slug=slugify(title),
                      creator=user)
    db.add(other_poll)
    db.commit()
    data = get_list_of_my_polls(active_user, db, '/api/polls', 2, 1)
    assert data['count'] == 1
    assert data['results'][0].id == poll.id


def test_create_new_option(poll, active_user, db):
    option = CreateOptionSchema(label='test option')
    new_option = create_option(poll.slug, active_user, option, db)
    assert new_option.label == option.label
    assert new_option.poll.id == poll.id


def test_create_new_option_for_non_existed_poll(active_user, db):
    option = CreateOptionSchema(label='test option')
    with pytest.raises(HTTPException):
        create_option('sadfadsf', active_user, option, db)


def test_create_new_option_for_not_mine_poll(user, poll, db):
    option = CreateOptionSchema(label='test option')
    with pytest.raises(HTTPException):
        create_option('sadfadsf', user, option, db)


def test_get_places_number_from_64():
    places = get_places_from(64)
    assert [64, 32, 16, 8, 4, 2] == places


def test_get_places_number_from_80():
    places = get_places_from(80)
    assert [64, 32, 16, 8, 4, 2] == places


@pytest.mark.asyncio
async def test_send_statistics_request_to_service(full_poll, db, mocker):
    class MockedResponse:
        status_code = 400

        @staticmethod
        def json():
            return {}

    async def async_magic():
        return MockedResponse

    MagicMock.__await__ = lambda x: async_magic().__await__()
    mocker.patch('httpx.AsyncClient.post')
    options = full_poll.options
    options = [SelectOptionSchema(option_id=option.id, event_type='WON') for option in options]
    resp = await send_selected_options_to_statistics(options, full_poll.slug, db)
    httpx.AsyncClient.post.assert_called_once()
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_send_statistics_request_with_wrong_option(full_poll, option, db, mocker):
    async def async_magic():
        pass

    MagicMock.__await__ = lambda x: async_magic().__await__()
    mocker.patch('httpx.AsyncClient.post')
    options = full_poll.options
    options = [SelectOptionSchema(option_id=option.id, event_type='WON') for option in options]
    options.append(SelectOptionSchema(option_id=option.id, event_type="TOOK_PART"))
    with pytest.raises(HTTPException):
        await send_selected_options_to_statistics(options, full_poll.slug, db)
    httpx.AsyncClient.post.assert_not_called()
