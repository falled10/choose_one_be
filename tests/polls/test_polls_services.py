import pytest
from fastapi.exceptions import HTTPException
from slugify import slugify

from api.polls.services import create_new_poll, update_poll, delete_poll
from api.polls.validators import validate_unique_title, validate_is_owner, validate_existed_poll
from api.polls.models import Poll
from api.polls.schemas import PatchUpdatePollSchema, CreatePollSchema
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
