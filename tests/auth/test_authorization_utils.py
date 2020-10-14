import pytest
import jwt

from datetime import datetime, timedelta

from fastapi.exceptions import HTTPException

from api.auth.authorization import get_current_user, \
    get_data_form_token, get_refresh_token, get_access_token, refresh_tokens, authorize_user, \
    _generate_token, _decode_token
from api.auth.dependencies import jwt_required
from api.auth.schemas import UserLoginSchema
from core.settings import SECRET_KEY, JWT_ALGORITHM


def test_generate_token(active_user):
    token = _generate_token(active_user, 'something', 12)
    data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert data['type'] == 'something'
    assert data['user_id'] == active_user.id


def test_decode_token(active_user):
    token = get_access_token(active_user)
    data = _decode_token(token)
    assert data['user_id'] == active_user.id
    assert data['type'] == 'access'


def test_decode_none():
    with pytest.raises(HTTPException):
        _decode_token('')


def test_decode_invalid_token():
    with pytest.raises(HTTPException):
        _decode_token('asdfadsfadsf')


def test_decode_expired_token():
    token = jwt.encode({
        'something': 'here',
        'exp': datetime.utcnow() - timedelta(minutes=1)
    }, SECRET_KEY, algorithm=JWT_ALGORITHM)
    with pytest.raises(HTTPException):
        _decode_token(token)


def test_get_current_user(active_user):
    obj = get_current_user({'user_id': active_user.id, 'type': 'access'})
    assert obj.email == active_user.email


def test_get_non_existed_user():
    with pytest.raises(HTTPException):
        get_current_user({'user_id': 123555})


def test_get_data_from_token():
    token = jwt.encode({
        'something': 'here',
        'exp': datetime.utcnow() + timedelta(minutes=12)
    }, SECRET_KEY, algorithm=JWT_ALGORITHM).decode()
    token_string = f"JWT {token}"
    data = get_data_form_token(token_string)
    assert data['something'] == 'here'


def test_get_data_from_expired_token():
    with pytest.raises(HTTPException):
        token = jwt.encode({
            'something': 'here',
            'exp': datetime.utcnow() - timedelta(minutes=1)
        }, SECRET_KEY, algorithm=JWT_ALGORITHM)
        token_string = f"JWT {token}"
        get_data_form_token(token_string)


def test_get_data_from_wrong_token():
    with pytest.raises(HTTPException):
        token_string = "JWT something"
        get_data_form_token(token_string)


def test_get_data_from_token_with_wrong_prefix():
    with pytest.raises(HTTPException):
        token = jwt.encode({
            'something': 'here',
            'exp': datetime.utcnow() - timedelta(minutes=1)
        }, SECRET_KEY, algorithm=JWT_ALGORITHM)
        token_string = f"something {token}"
        get_data_form_token(token_string)


def test_get_access_token(active_user):
    token = get_access_token(active_user)
    data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert data['user_id'] == active_user.id
    assert data['type'] == 'access'


def test_get_refresh_token(active_user):
    token = get_refresh_token(active_user)
    data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert data['user_id'] == active_user.id
    assert data['type'] == 'refresh'


def test_refresh_tokens(active_user, db):
    token = get_refresh_token(active_user)
    data = refresh_tokens(token, db)
    assert 'access' in data
    assert 'refresh' in data
    access_data = jwt.decode(data['access'], SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert access_data['user_id'] == active_user.id


def test_refresh_tokens_with_access_token(active_user, db):
    token = get_access_token(active_user)
    with pytest.raises(HTTPException):
        refresh_tokens(token, db)


def test_refresh_tokens_with_wrong_woken(db):
    with pytest.raises(HTTPException):
        refresh_tokens('asdfasdfadsf', db)


def test_refresh_tokens_user_is_unactive(user, db):
    token = get_refresh_token(user)
    with pytest.raises(HTTPException):
        refresh_tokens(token, db)


def test_refresh_tokens_token_is_expired(active_user, db):
    token = jwt.encode({'type': 'refresh', 'user_id': active_user.id,
                        'exp': datetime.utcnow() - timedelta(minutes=1)},
                       SECRET_KEY, algorithm=JWT_ALGORITHM)
    with pytest.raises(HTTPException):
        refresh_tokens(token, db)


def test_authorize_user(active_user, db):
    data = authorize_user(UserLoginSchema(email=active_user.email,
                                          password='testpass123'), db)
    assert 'access' in data
    assert 'refresh' in data
    access_data = jwt.decode(data['access'], SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert access_data['user_id'] == active_user.id


def test_authorize_user_is_inactive(user, db):
    with pytest.raises(HTTPException):
        authorize_user(UserLoginSchema(email=user.email,
                                       password='testpass123'), db)


def test_authorize_user_invalid_creds(db):
    with pytest.raises(HTTPException):
        authorize_user(UserLoginSchema(email='random@mail.com',
                                       password='12321313'), db)


def test_jwt_required_dependency(active_user):
    token = get_access_token(active_user)
    token = f'JWT {token}'
    user = jwt_required(token)
    assert user.id == active_user.id


def test_jwt_required_without_token():
    with pytest.raises(HTTPException):
        jwt_required(None)


def test_jwt_required_refresh_token(active_user):
    token = get_refresh_token(active_user)
    token = f'JWT {token}'
    with pytest.raises(HTTPException):
        jwt_required(token)


def test_jwt_required_invalid_token():
    with pytest.raises(HTTPException):
        jwt_required('asdfadsfadsf')
