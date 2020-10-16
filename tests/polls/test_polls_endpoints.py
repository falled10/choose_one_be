from slugify import slugify

from api.polls.models import Poll
from api.polls.schemas import CreatePollSchema
from api.polls.services import create_new_poll


def test_create_new_poll(client, db, token_header):
    data = {
        'title': 'new_poll',
        'description': 'some new description',
        'media_type': 'GIF'
    }
    resp = client.post('/api/polls', json=data, headers=token_header)
    assert resp.status_code == 201
    assert 'id' in resp.json()
    assert db.query(Poll).get(resp.json()['id'])
    assert 'slug' in resp.json()


def test_create_new_poll_non_authorized(client, db):
    data = {
        'title': 'new_poll',
        'description': 'some new description',
        'media_type': 'GIF'
    }
    resp = client.post('/api/polls', json=data)
    assert resp.status_code == 401


def test_create_new_poll_with_title_that_already_exists(client, db, token_header, poll):
    data = {
        'title': poll.title,
        'description': 'some new description',
        'media_type': 'GIF'
    }
    resp = client.post('/api/polls', json=data, headers=token_header)
    assert resp.status_code == 400


def test_create_new_poll_without_title(client, db, token_header):
    data = {
        'description': 'some new description',
        'media_type': 'GIF'
    }
    resp = client.post('/api/polls', json=data, headers=token_header)
    assert resp.status_code == 400


def test_update_existed_poll(client, db, token_header, poll):
    data = {
        'title': 'some new title'
    }
    resp = client.patch(f'/api/polls/{poll.slug}', json=data, headers=token_header)
    assert resp.status_code == 200
    assert resp.json()['title'] == data['title']
    db.refresh(poll)
    assert poll.title == data['title']
    assert poll.slug == slugify(data['title'])


def test_update_existed_poll_non_authorized(client, db, poll):
    data = {
        'title': 'some new title'
    }
    resp = client.patch(f'/api/polls/{poll.slug}', json=data)
    assert resp.status_code == 401


def test_update_existed_poll_from_another_user(client, user, db, token_header, poll):
    poll.creator = user
    db.commit()
    db.refresh(poll)
    data = {
        'title': 'some new title'
    }
    resp = client.patch(f'/api/polls/{poll.slug}', json=data, headers=token_header)
    assert resp.status_code == 403


def test_update_non_existed_poll(client, db, token_header):
    data = {
        'title': 'some new title'
    }
    resp = client.patch('/api/polls/asdfasdfasdf', json=data, headers=token_header)
    assert resp.status_code == 404


def test_update_existed_poll_with_the_same_title(client, user, db, token_header, poll):
    data = CreatePollSchema(title='some another title', description='some another description')
    another_poll = create_new_poll(data, user, db)
    data = {
        'title': poll.title
    }
    resp = client.patch(f'/api/polls/{another_poll.slug}', json=data, headers=token_header)
    assert resp.status_code == 400


def test_delete_existed_poll(client, db, token_header, poll):
    resp = client.delete(f'api/polls/{poll.slug}', headers=token_header)
    assert resp.status_code == 204
    assert not db.query(Poll).filter_by(id=poll.id).first()


def test_delete_not_existed_poll(client, token_header):
    resp = client.delete('api/polls/asdfsdf', headers=token_header)
    assert resp.status_code == 404


def test_delete_not_your_poll(client, db, token_header, user):
    data = CreatePollSchema(title='some another title', description='some another description')
    another_poll = create_new_poll(data, user, db)
    resp = client.delete(f'api/polls/{another_poll.slug}', headers=token_header)
    assert resp.status_code == 403


def test_delete_poll_when_not_logged_in(client, poll):
    resp = client.delete(f'api/polls/{poll.slug}')
    assert resp.status_code == 401
