import mailjet_rest

from core.tasks import send_email


def test_send_email_task(mocker):
    mail_data = {
        'subject': 'ChooseOne activate user',
        'template': 'activate_user.html',
        'context': {'url': 'http://localhost:8000/'},
        'recipients': ['test@mail.com'],
    }

    def return_mock_class(*args, **kwargs):
        class MockRequest:
            status_code = 200

        return MockRequest()
    mocker.patch('mailjet_rest.client.api_call', side_effect=return_mock_class)
    send_email(**mail_data)
    mailjet_rest.client.api_call.assert_called_once()
