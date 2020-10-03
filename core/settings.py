from environs import Env


env = Env()
env.read_env()


PROJECT_LOG_PATH = env.path('PROJECT_LOG_PATH')
LOGS_ROTATION = '500 MB'

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
            'models': ['api.users.models', 'aerich.models'],
            # If no default_connection specified, defaults to 'default'
            'default_connection': 'default',
        }
    }
}
