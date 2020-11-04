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
