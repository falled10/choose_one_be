from __future__ import absolute_import, unicode_literals

import celery
from celery import Celery


@celery.signals.setup_logging.connect
def on_celery_setup_logging(**kwargs):
    pass


app = Celery('choose_one')

app.config_from_object('core.settings', namespace='CELERY')
app.conf.update()
app.autodiscover_tasks(['core'])
