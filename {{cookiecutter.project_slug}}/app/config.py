import os

ENV = os.getenv('ENV', 'production')
if ENV not in ('production', 'development', 'testing'):
    raise ValueError(f"{ENV} should be 'production', 'development' or 'testing'")
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
