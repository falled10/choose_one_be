from celery import shared_task
from celery.exceptions import MaxRetriesExceededError, SoftTimeLimitExceeded
from jinja2 import FileSystemLoader, Environment
from mailjet_rest import Client

from core.settings import MAILJET_PUBLIC_KEY, MAILJET_SECRET_KEY, MAILJET_USER
from core.logger import celery_logger


MAILJET_API_VERSION = 'v3.1'


@shared_task(bind=True, max_retries=3)
def send_email(self, subject, template, recipients, context):
    """
    Sending email
    :param self:
    :param subject: message title
    :param template: name of template
    :param recipients: list of recipients
    :param context: message data in dict format
    """
    mailjet = Client(auth=(MAILJET_PUBLIC_KEY, MAILJET_SECRET_KEY), version=MAILJET_API_VERSION)
    recipients = [{'Email': recipient} for recipient in recipients]
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    template = env.get_template(template)

    message = template.render(context)
    data = {
        'Messages': [
            {
                'From': {
                    'Email': MAILJET_USER,
                    'Name': 'Choose One Support'
                },
                'To': recipients,
                'Subject': subject,
                'HTMLPart': message
            }
        ]
    }
    try:
        result = mailjet.send.create(data=data)
    except SoftTimeLimitExceeded as e:
        celery_logger.error(e)
        return
    celery_logger.info(f"Email notification sent to {recipients}")

    if result.status_code != 200:
        error = result.json()
        celery_logger.error(f"Something went wrong while send email, Error: {error}")
        try:
            self.retry(countdown=30)
        except MaxRetriesExceededError as e:
            celery_logger.error(e)
