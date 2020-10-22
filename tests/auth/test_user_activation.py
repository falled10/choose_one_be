import pytest
import jwt


from api.auth.utils import generate_activation_token
from api.auth.services import activate_user
from api.users.models import User
from core.exceptions import CustomValidationError
from core.settings import SECRET_KEY, JWT_ALGORITHM


def test_generate_activation_token(user):
    token = generate_activation_token(user.email)
    data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert data['user_email'] == user.email


def test_activate_inactive_user(user, db):
    token = generate_activation_token(user.email)
    assert not user.is_active
    activate_user(token, db)
    user = db.query(User).get(user.id)
    assert user.is_active


def test_activate_inactive_user_invalid_token(db):
    with pytest.raises(CustomValidationError):
        activate_user('asdfadsfasdf', db)


def test_activate_user_endpoint(user, client, db):
    token = generate_activation_token(user.email)
    data = {
        'token': token
    }
    assert not user.is_active
    resp = client.post('/api/auth/activate', json=data)
    assert resp.status_code == 204
    db.refresh(user)
    assert user.is_active


def test_activate_already_active_user(user, client, db):
    user.is_active = True
    db.commit()
    token = generate_activation_token(user.email)
    data = {
        'token': token
    }
    resp = client.post('/api/auth/activate', json=data)
    assert resp.status_code == 400


def test_invalid_token_for_activate_user(client):
    resp = client.post('/api/auth/activate', json={"token": "asdfadsfadsf"})
    assert resp.status_code == 400
