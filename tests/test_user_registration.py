import pytest

from api.users.models import User
from api.auth.validators import validate_unique_email, validate_unique_username

from core.tasks import send_email
from core.exceptions import CustomValidationError


def test_user_registration(mocker, client, event_loop):
    mocker.patch('core.tasks.send_email.delay')
    data = {
        'username': 'test_user',
        'email': 'test@mail.com',
        'password': 'testpass123'
    }
    resp = client.post('/api/auth/register', json=data)
    assert resp.status_code == 201
    assert 'id' in resp.json()
    user = event_loop.run_until_complete(User.get(id=resp.json()['id']))
    assert user.email == resp.json()['email']
    assert not user.is_active
    send_email.delay.assert_called_once()


def test_user_registration_invalid_data(client):
    data = {
        'username': 'asdfasdf',
        'email': 'sadfadsfads',
        'password': ''
    }
    resp = client.post('/api/auth/register', json=data)
    assert resp.status_code == 400


def test_user_registration_with_already_existed_email(mocker, client, event_loop):
    mocker.patch('core.tasks.send_email.delay')
    data = {
        'username': 'test_user',
        'email': 'test@mail.com',
        'password': 'testpass123'
    }
    resp1 = client.post('/api/auth/register', json=data)
    data['username'] = 'another_user'
    resp = client.post('/api/auth/register', json=data)
    assert resp.status_code == 400
    assert event_loop.run_until_complete(User.filter(email=data['email']).exists())
    assert 'email' in resp.json()


def test_user_registration_with_already_existed_username(mocker, client):
    mocker.patch('core.tasks.send_email.delay')
    data = {
        'username': 'test_user',
        'email': 'test@mail.com',
        'password': 'testpass123'
    }
    client.post('/api/auth/register', json=data)
    data['email'] = 'another@mail.com'
    resp = client.post('/api/auth/register', json=data)
    assert resp.status_code == 400
    assert 'username' in resp.json()


@pytest.mark.asyncio
async def test_validation_raise_error_that_email_exists(user):
    with pytest.raises(CustomValidationError):
        await validate_unique_email(user.email)
