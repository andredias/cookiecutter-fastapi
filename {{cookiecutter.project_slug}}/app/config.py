import os
import secrets
from datetime import timedelta

ENV = os.getenv('ENV', 'production').lower()
if ENV not in ('production', 'development', 'testing'):
    raise ValueError(
        f'ENV={ENV} is not valid. '
        "It should be 'production', 'development' or 'testing'"
    )
DEBUG = ENV != 'production'
TESTING = ENV == 'testing'

LOG_LEVEL = os.getenv('LOG_LEVEL') or DEBUG and 'DEBUG' or 'INFO'

DB_PASSWORD = os.getenv('DB_PASSWORD', 'development_1234')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT') or TESTING and '5431' or '5432'
DB_NAME = os.getenv('DB_NAME', '{{cookiecutter.project_slug}}')
DATABASE_URL = (
    os.getenv('DATABASE_URL')
    or f'postgresql://postgres:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_URL = os.getenv('REDIS_URL') or f'redis://{REDIS_HOST}:{REDIS_PORT}'

SECRET_KEY = bytes(os.getenv('SECRET_KEY', ''), 'utf-8') or secrets.token_bytes(
    32
)
SESSION_ID_LENGTH = int(os.getenv('SESSION_ID_LENGTH', 16))
SESSION_LIFETIME = int(timedelta(days=7).total_seconds())

PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 15))
PASSWORD_MIN_VARIETY = int(os.getenv('PASSWORD_MIN_VARIETY', 5))
