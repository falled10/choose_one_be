from api.users.models import User

from core.tasks import send_email


def test_user_registration(mocker, client, db):
    mocker.patch('core.tasks.send_email.delay')
    data = {
        'username': 'test_user',
        'email': 'test@mail.com',
        'password': 'testpass123'
    }
    resp = client.post('/api/auth/register', json=data)
    assert resp.status_code == 201
    assert 'id' in resp.json()
    user = db.query(User).get(resp.json()['id'])
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


def test_user_registration_with_already_existed_email(mocker, client, db):
    mocker.patch('core.tasks.send_email.delay')
    data = {
        'username': 'test_user',
        'email': 'test@mail.com',
        'password': 'testpass123'
    }
    client.post('/api/auth/register', json=data)
    data['username'] = 'another_user'
    resp = client.post('/api/auth/register', json=data)
    assert resp.status_code == 400
    assert db.query(db.query(User).filter(User.email == data['email']).exists())
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

