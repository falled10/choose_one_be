from environs import Env


env = Env()
env.read_env()


PROJECT_LOG_PATH = env.path('PROJECT_LOG_PATH')
CELERY_LOG_PATH = env.path('CELERY_LOG_PATH')
LOGS_ROTATION = '500 MB'

TORTOISE_MODELS_LIST = ['api.users.models', 'aerich.models']

TORTOISE_CONFIG = {
    'connections': {
        # Dict format for connection
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': env.str('DB_HOST'),
                'port': env.str('DB_PORT'),
                'user': env.str('POSTGRES_USER'),
                'password': env.str('POSTGRES_PASSWORD'),
                'database': env.str('POSTGRES_DB'),
            }
        },
    },
    'apps': {
        'models': {
            'models': TORTOISE_MODELS_LIST,
            # If no default_connection specified, defaults to 'default'
            'default_connection': 'default',
        }
    }
}


CELERY_BROKER_URL = env.str('BROKER_URL', '')
CELERY_TASK_DEFAULT_QUEUE = "fastapi"

CELERY_TASK_SOFT_TIME_LIMIT = env.int('TASK_SOFT_TIME_LIMIT_SEC', 40)

MAILJET_PUBLIC_KEY = env.str('MAILJET_PUBLIC_KEY')
MAILJET_SECRET_KEY = env.str('MAILJET_SECRET_KEY')
MAILJET_USER = env.str('MAILJET_USER')


SECRET_KEY = env.str('SECRET_KEY')
JWT_ALGORITHM = env.str('JWT_ALGORITHM', 'HS256')
JWT_PREFIX = "JWT"
JWT_TOKEN_LIFE_TIME = env.int('JWT_TOKEN_LIFE_TIME', 15)
JWT_REFRESH_TOKEN_LIFE_TIME = env.int('JWT_REFRESH_TOKEN_LIFE_TIME', 60)
USER_ACTIVATION_URL = env.str('USER_ACTIVATION_URL', 'http://localhost:8000/')
