from environs import Env


env = Env()
env.read_env()


PROJECT_LOG_PATH = env.path('PROJECT_LOG_PATH', '.data/project.log')
CELERY_LOG_PATH = env.path('CELERY_LOG_PATH', '.data/celery.log')
LOGS_ROTATION = '500 MB'

USER = env.str('POSTGRES_USER')
PASSWORD = env.str('POSTGRES_PASSWORD')
HOST = env.str('DB_HOST')
PORT = env.str('DB_PORT')
DB = env.str('POSTGRES_DB')

DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'

CELERY_BROKER_URL = env.str('BROKER_URL', '')
ELASTICSEARCH_URL = env.str('ELASTICSEARCH_URL', 'http://localhost:9200')
CELERY_TASK_DEFAULT_QUEUE = "fastapi"

CELERY_TASK_SOFT_TIME_LIMIT = env.int('TASK_SOFT_TIME_LIMIT_SEC', 40)

MAILJET_PUBLIC_KEY = env.str('MAILJET_PUBLIC_KEY', '')
MAILJET_SECRET_KEY = env.str('MAILJET_SECRET_KEY', '')
MAILJET_USER = env.str('MAILJET_USER', '')


SECRET_KEY = env.str('SECRET_KEY')
JWT_ALGORITHM = env.str('JWT_ALGORITHM', 'HS256')
JWT_PREFIX = "JWT"
JWT_TOKEN_LIFE_TIME = env.int('JWT_TOKEN_LIFE_TIME', 15)
JWT_REFRESH_TOKEN_LIFE_TIME = env.int('JWT_REFRESH_TOKEN_LIFE_TIME', 60)
USER_ACTIVATION_URL = env.str('USER_ACTIVATION_URL', 'http://localhost:8000/')
PASSWORD_RESET_URL = env.str('PASSWORD_RESET_URL', 'http://localhost:8000/')

CORS_ORIGINS = env.list('CORS_ORIGINS', ['*'])

MIN_PLACES_NUMBER = env.int('MIN_PLACES_NUMBER', 8)
MAX_PLACES_NUMBER = env.int('MAX_PLACES_NUMBER', 512)
TEST_MODE = env.bool('TEST_MODE', False)
STATISTICS_SERVICE_URL = env.str('STATISTICS_SERVICE_URL', 'http://localhost:8001')
