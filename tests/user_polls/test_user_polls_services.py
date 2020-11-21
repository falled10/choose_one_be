import pytest

from sqlalchemy.orm.session import SessionTransaction

from api.user_polls.services import create_user_poll
from api.user_polls.schemas import UserPollSchema


@pytest.mark.asyncio
async def test_create_new_poll_if_exception_nothing_is_created(mocker, full_poll, active_user, db):
    options = full_poll.options
    data = {
        'poll_id': full_poll.id,
        'options': [{'option_id': option.id, 'place_number': i}
                    for i, option in enumerate(options, 1)]
    }

    def custom_bulk_save_objects(*args, **kwargs):
        raise ValueError

    mocker.patch('sqlalchemy.orm.Session.bulk_insert_mappings', side_effect=custom_bulk_save_objects)
    mocker.patch('sqlalchemy.orm.session.SessionTransaction.rollback')
    data = UserPollSchema(**data)
    await create_user_poll(data, active_user, db)
    SessionTransaction.rollback.assert_called_once()
