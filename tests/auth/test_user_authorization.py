from api.auth.authorization import get_refresh_token, get_access_token


def test_login_user(client, active_user):
    data = {
        'email': active_user.email,
        'password': 'testpass123'
    }
    resp = client.post('/api/auth/login', json=data)
    assert resp.status_code == 200
    assert 'access' in resp.json()
    assert 'refresh' in resp.json()


def test_login_user_invalid_data(client):
    data = {
        'email': 'non_existed@mail.com',
        'password': 'testpass123'
    }
    resp = client.post('/api/auth/login', json=data)
    assert resp.status_code == 401


def test_login_user_non_active_user(client, user):
    data = {
        'email': user.email,
        'password': 'testpass123'
    }
    resp = client.post('/api/auth/login', json=data)
    assert resp.status_code == 401


def test_refresh_tokens(client, active_user):
    token = get_refresh_token(active_user)
    data = {
        'refresh': token
    }
    resp = client.post('/api/auth/refresh', json=data)
    assert resp.status_code == 200
    assert 'access' in resp.json()
    assert 'refresh' in resp.json()


def test_refresh_tokens_with_access_token(client, active_user):
    token = get_access_token(active_user)
    data = {
        'refresh': token
    }
    resp = client.post('/api/auth/refresh', json=data)
    assert resp.status_code == 401


def test_refresh_token_for_non_active_user(client, user):
    token = get_refresh_token(user)
    data = {
        'refresh': token
    }
    resp = client.post('/api/auth/refresh', json=data)
    assert resp.status_code == 401


def test_refresh_invalid_token(client):
    token = 'asdfasdf'
    data = {
        'refresh': token
    }
    resp = client.post('/api/auth/refresh', json=data)
    assert resp.status_code == 401
