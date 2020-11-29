from unittest.mock import MagicMock

import httpx
from werkzeug.security import check_password_hash

from api.auth.utils import generate_token
from core.tasks import send_email


def test_get_current_user_profile(active_user, client, token_header):
    resp = client.get('api/profile', headers=token_header)
    data = resp.json()
    assert resp.status_code == 200
    assert data['id'] == active_user.id


def test_get_current_user_when_logged_out(client):
    resp = client.get('api/profile')
    assert resp.status_code == 401


def test_send_forget_password_email(mocker, user, client):
    mocker.patch('core.tasks.send_email.delay')
    data = {
        'email': user.email
    }
    resp = client.post('api/profile/password/forget', json=data)
    assert resp.status_code == 204
    send_email.delay.assert_called_once()


def test_send_forget_password_email_does_not_exists(mocker, client):
    mocker.patch('core.tasks.send_email.delay')
    data = {
        'email': 'non_existed@mail.com'
    }
    resp = client.post('api/profile/password/forget', json=data)
    assert resp.status_code == 400
    send_email.delay.assert_not_called()


def test_reset_password(user, client, db):
    token = generate_token(user.email, 'forget_password')
    data = {
        'new_password': 'some_new_password',
        'confirmed_password': 'some_new_password',
        'token': token
    }
    resp = client.post('api/profile/password/reset', json=data)
    assert resp.status_code == 204
    db.refresh(user)
    assert check_password_hash(user.password, data['new_password'])


def test_reset_password_passwords_does_not_match(user, client, db):
    token = generate_token(user.email, 'forget_password')
    data = {
        'new_password': 'some_new_password',
        'confirmed_password': 'some_other_password',
        'token': token
    }
    resp = client.post('api/profile/password/reset', json=data)
    assert resp.status_code == 400


def test_get_user_recommendations(client, token_header, mocker):
    class MockedResponse:

        @staticmethod
        def json():
            return []

    async def async_magic():
        return MockedResponse

    MagicMock.__await__ = lambda x: async_magic().__await__()
    mocker.patch('httpx.AsyncClient.get', return_value=MockedResponse)
    resp = client.get('api/profile/my-recommendations', headers=token_header)
    assert resp.status_code == 200
    httpx.AsyncClient.get.assert_called_once()


def test_get_user_recommendations_as_anon_user(client):
    resp = client.get('api/profile/my-recommendations')
    assert resp.status_code == 401
