from unittest.mock import MagicMock

from slugify import slugify
from httpx import AsyncClient

from api.polls.models import Poll, Option
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


def test_update_existed_poll_with_the_same_title(client, active_user, db, token_header, poll):
    data = CreatePollSchema(title='some another title', description='some another description')
    another_poll = create_new_poll(data, active_user, db)
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


def test_get_single_poll_by_slug(client, poll, token_header):
    resp = client.get(f'api/polls/{poll.slug}', headers=token_header)
    assert resp.status_code == 200
    assert resp.json()['id'] == poll.id


def test_get_single_poll_when_logged_out(client, poll):
    resp = client.get(f'api/polls/{poll.slug}')
    assert resp.status_code == 200
    assert resp.json()['id'] == poll.id


def test_get_non_existed_poll(client):
    resp = client.get('api/polls/asdfadsf')
    assert resp.status_code == 404


def test_get_list_of_polls(poll, client):
    resp = client.get('api/polls')
    assert resp.status_code == 200
    assert resp.json()['count'] == 1
    assert resp.json()['results'][0]['id'] == poll.id


def test_get_list_of_polls_without_poll(client):
    resp = client.get('api/polls')
    assert resp.json()['count'] == 0
    assert resp.json()['results'] == []


def test_get_list_of_polls_wrong_page_size(poll, client):
    resp = client.get('api/polls?page_size=0')
    assert resp.status_code == 400


def test_get_my_polls(poll, client, token_header):
    resp = client.get('api/polls/my-polls', headers=token_header)
    assert resp.status_code == 200
    assert resp.json()['count'] == 1
    assert resp.json()['results'][0]['id'] == poll.id


def test_get_my_polls_when_logged_out(poll, client):
    resp = client.get('api/polls/my-polls')
    assert resp.status_code == 401


def test_get_my_polls_when_there_is_no_my_polls(poll, db, user, client, token_header):
    poll.creator = user
    db.commit()

    resp = client.get('api/polls/my-polls', headers=token_header)
    assert resp.status_code == 200
    assert resp.json()['count'] == 0


def test_create_new_option(poll, token_header, client, db):
    data = {
        'label': 'some new option'
    }
    resp = client.post(f'api/polls/{poll.slug}/options', json=data, headers=token_header)
    assert resp.status_code == 201
    assert resp.json()['label'] == data['label']
    assert resp.json()['id']
    option = db.query(Option).get(resp.json()['id'])
    assert option.poll.id == poll.id


def test_create_new_option_for_non_existed_poll(token_header, client):
    data = {
        'label': 'some new option'
    }
    resp = client.post('api/polls/12321312313/options', json=data, headers=token_header)
    assert resp.status_code == 404


def test_create_new_option_when_logged_out(poll, client):
    data = {
        'label': 'some new option'
    }
    resp = client.post(f'api/polls/{poll.slug}/options', json=data)
    assert resp.status_code == 401


def test_create_new_option_for_another_users_poll(poll, user, client, token_header, db):
    poll.creator = user
    db.commit()
    data = {
        'label': 'some new option'
    }
    resp = client.post(f'api/polls/{poll.slug}/options', json=data, headers=token_header)
    assert resp.status_code == 403


def test_delete_exited_option(poll, option, client, token_header, db, mocker):
    async def async_magic():
        pass

    MagicMock.__await__ = lambda x: async_magic().__await__()
    mocker.patch('httpx.AsyncClient.delete')
    resp = client.delete(f'api/polls/{poll.slug}/options/{option.id}', headers=token_header)
    assert resp.status_code == 204
    assert not db.query(Option).filter_by(id=option.id).first()
    AsyncClient.delete.assert_called_once()


def test_delete_non_exited_option(poll, client, token_header):
    resp = client.delete(f'api/polls/{poll.slug}/options/12', headers=token_header)
    assert resp.status_code == 404


def test_delete_option_of_ono_existed_poll(client, token_header):
    resp = client.delete('api/polls/asdfasf/options/12', headers=token_header)
    assert resp.status_code == 404


def test_delete_option_of_poll_from_another_user(poll, user, token_header, client, db, option):
    poll.creator = user
    db.commit()
    resp = client.delete(f'api/polls/{poll.slug}/options/{option.id}', headers=token_header)
    assert resp.status_code == 403


def test_delete_option_of_poll_when_user_is_logged_out(poll, client, option):
    resp = client.delete(f'api/polls/{poll.slug}/options/{option.id}')
    assert resp.status_code == 401


def test_update_existed_option(poll, option, client, db, token_header):
    data = {
        'label': 'new updated label'
    }
    old_label = option.label
    resp = client.patch(f'api/polls/{poll.slug}/options/{option.id}', json=data, headers=token_header)
    assert resp.status_code == 200
    db.refresh(option)
    assert option.label == data['label']
    assert option.label != old_label


def test_update_option_invalid_data(poll, option, client, token_header):
    data = {
        'label': None
    }
    resp = client.patch(f'api/polls/{poll.slug}/options/{option.id}', json=data, headers=token_header)
    assert resp.status_code == 400


def test_update_option_when_logged_out(poll, option, client):
    data = {
        'label': 'new updated label'
    }
    resp = client.patch(f'api/polls/{poll.slug}/options/{option.id}', json=data)
    assert resp.status_code == 401


def test_get_all_polls_options(poll, option, client):
    resp = client.get(f'api/polls/{poll.slug}/options')
    data = resp.json()
    assert resp.status_code == 200
    assert data[0]['id'] == option.id


def test_get_only_one_poll_option(full_poll, client):
    resp = client.get(f'api/polls/{full_poll.slug}/options?places_number=1')
    data = resp.json()
    assert resp.status_code == 200
    assert len(data) == 1


def test_get_all_polls_non_existed_poll(client):
    resp = client.get('api/polls/sadfasdf/options')
    assert resp.status_code == 404


def test_get_places_number_of_poll(client, full_poll):
    resp = client.get(f'api/polls/{full_poll.slug}/places-numbers')
    assert resp.status_code == 200
    assert resp.json() == [2]


def test_get_places_number_to_few_options(client, poll):
    resp = client.get(f'api/polls/{poll.slug}/places-numbers')
    assert resp.status_code == 400


def test_get_statistics_as_unauthorized_user(client, full_poll, token_header, db, mocker):
    class MockedResponse:

        @staticmethod
        def json():
            return []

    async def async_magic():
        return MockedResponse

    options = full_poll.options
    data = {
        'poll_id': full_poll.id,
        'options': [{'option_id': option.id}
                    for option in options]
    }
    MagicMock.__await__ = lambda x: async_magic().__await__()
    mocker.patch('httpx.AsyncClient.post', return_value=MockedResponse)
    resp = client.post('api/polls/statistics', headers=token_header, json=data)
    assert resp.status_code == 200
    AsyncClient.post.assert_called_once()
