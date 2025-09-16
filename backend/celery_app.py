from flask import Flask
from extensions import celery

def make_celery(app):
    celery.conf.update({
        'broker_url': app.config['CELERY_BROKER_URL'],
        'result_backend': app.config['CELERY_RESULT_BACKEND'],
        'beat_schedule': app.config.get('CELERY_BEAT_SCHEDULE', {}),
        'beat_scheduler': 'celery.beat.Scheduler',
        'task_serializer': app.config.get('CELERY_TASK_SERIALIZER', 'json'),
        'result_serializer': app.config.get('CELERY_RESULT_SERIALIZER', 'json'),
        'accept_content': app.config.get('CELERY_ACCEPT_CONTENT', ['json']),
        'timezone': app.config.get('CELERY_TIMEZONE', 'UTC'),
        'enable_utc': app.config.get('CELERY_ENABLE_UTC', True),
        'result_expires': app.config.get('CELERY_RESULT_EXPIRES', 3600),
        'task_track_started': app.config.get('CELERY_TASK_TRACK_STARTED', True),
        'task_time_limit': app.config.get('CELERY_TASK_TIME_LIMIT', 1800),
        'task_always_eager': app.config.get('CELERY_TASK_ALWAYS_EAGER', False),
        'task_eager_propagates': app.config.get('CELERY_TASK_EAGER_PROPAGATES', False),
    })

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
