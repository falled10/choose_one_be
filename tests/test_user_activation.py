import pytest
import jwt


from api.auth.utils import generate_activation_token
from api.auth.service import activate_user
from api.users.models import User
from core.exceptions import CustomValidationError
from core.settings import SECRET_KEY, JWT_ALGORITHM


def test_generate_activation_token(user):
    token = generate_activation_token(user.email)
    data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert data['user_email'] == user.email


@pytest.mark.asyncio
async def test_activate_inactive_user(user):
    token = generate_activation_token(user.email)
    assert not user.is_active
    await activate_user(token)
    user = await User.get(id=user.id)
    assert user.is_active


@pytest.mark.asyncio
async def test_activate_inactive_user_invalid_token():
    with pytest.raises(CustomValidationError):
        await activate_user('asdfadsfasdf')


def test_activate_user_endpoint(user, client, event_loop):
    token = generate_activation_token(user.email)
    data = {
        'token': token
    }
    assert not user.is_active
    resp = client.post('/api/auth/activate', json=data)
    assert resp.status_code == 204
    user = event_loop.run_until_complete(User.get(id=user.id))
    assert user.is_active


def test_activate_already_active_user(user, client, event_loop):
    user.is_active = True
    event_loop.run_until_complete(user.save())
    token = generate_activation_token(user.email)
    data = {
        'token': token
    }
    resp = client.post('/api/auth/activate', json=data)
    assert resp.status_code == 400


def test_invalid_token_for_activate_user(client):
    resp = client.post('/api/auth/activate', json={"token": "asdfadsfadsf"})
    assert resp.status_code == 400
