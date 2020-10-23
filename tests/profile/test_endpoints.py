def test_get_current_user_profile(active_user, client, token_header):
    resp = client.get('api/profile', headers=token_header)
    data = resp.json()
    assert resp.status_code == 200
    assert data['id'] == active_user.id


def test_get_current_user_when_logged_out(client):
    resp = client.get('api/profile')
    assert resp.status_code == 401
