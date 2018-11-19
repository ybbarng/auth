from celery import Celery

from auth.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from auth.utils import parse_jwt


auth_celery = Celery('auth',
             broker=CELERY_BROKER_URL,
             backend=CELERY_RESULT_BACKEND)

auth_celery.conf.timezone = 'Asia/Seoul'
auth_celery.conf.task_default_queue = 'auth'


@auth_celery.task(name='auth.is_authenticated')
def is_authenticated(jwt_data):
    return parse_jwt(jwt_data)


if __name__ == '__main__':
    auth_celery.start()
