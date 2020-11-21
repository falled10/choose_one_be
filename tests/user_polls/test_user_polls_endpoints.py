from unittest.mock import MagicMock

import httpx

from api.user_polls.models import UserOption


def test_create_new_user_poll(client, full_poll, token_header, db, mocker):
    class MockedResponse:
        status_code = 400

        @staticmethod
        def json():
            return []

    async def async_magic():
        return MockedResponse

    MagicMock.__await__ = lambda x: async_magic().__await__()
    mocker.patch('httpx.AsyncClient.post', return_value=MockedResponse)
    options = full_poll.options
    data = {
        'poll_id': full_poll.id,
        'options': [{'option_id': option.id}
                    for option in options]
    }
    resp = client.post('api/user-polls', headers=token_header, json=data)
    assert resp.status_code == 201
    assert db.query(UserOption).count() == 2
    httpx.AsyncClient.post.assert_called_once()


def test_create_new_user_poll_one_option_is_from_another_poll(client, full_poll,
                                                              token_header, db, poll):
    options = full_poll.options
    options[0].poll_id = poll.id
    db.commit()
    db.refresh(options[0])
    data = {
        'poll_id': full_poll.id,
        'options': [{'option_id': option.id, 'place_number': i}
                    for i, option in enumerate(options, 1)]
    }
    resp = client.post('api/user-polls', headers=token_header, json=data)
    assert resp.status_code == 400


def test_create_new_user_poll_poll_does_not_exists(client, full_poll, token_header):
    options = full_poll.options
    data = {
        'poll_id': 1233,
        'options': [{'option_id': option.id, 'place_number': i}
                    for i, option in enumerate(options, 1)]
    }
    resp = client.post('api/user-polls', headers=token_header, json=data)
    assert resp.status_code == 400


def test_create_new_user_poll_empty_options(client, full_poll, token_header, db, mocker):
    class MockedResponse:
        status_code = 400

        @staticmethod
        def json():
            return []

    async def async_magic():
        return MockedResponse

    MagicMock.__await__ = lambda x: async_magic().__await__()
    mocker.patch('httpx.AsyncClient.post', return_value=MockedResponse)
    data = {
        'poll_id': full_poll.id,
        'options': []
    }
    resp = client.post('api/user-polls', headers=token_header, json=data)
    assert resp.status_code == 201
    assert db.query(UserOption).count() == 0
    httpx.AsyncClient.post.assert_called_once()


def test_create_new_user_poll_some_option_does_not_exists(client, full_poll, token_header):
    options = full_poll.options
    data = {
        'poll_id': full_poll.id,
        'options': [{'option_id': option.id, 'place_number': i}
                    for i, option in enumerate(options, 1)]
    }
    data['options'][0]['option_id'] = 123
    resp = client.post('api/user-polls', headers=token_header, json=data)
    assert resp.status_code == 400
