import os
from subprocess import DEVNULL, check_call
from typing import AsyncIterable, Generator

from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from pytest import fixture

os.environ['ENV'] = 'testing'

from app.config import DB_NAME, DB_PASSWORD, DB_PORT  # noqa: E402
from app.main import app as _app  # noqa: E402


@fixture(scope='session')
def docker() -> Generator:
    check_call(
        f'docker run -d --rm -e POSTGRES_DB={DB_NAME} '
        f'-e POSTGRES_PASSWORD={DB_PASSWORD} '
        f'-p {DB_PORT}:5432 --name postgres-testing postgres:alpine',
        stdout=DEVNULL,
        shell=True,
    )
    try:
        yield
    finally:
        check_call(
            'docker stop -t 0 postgres-testing', stdout=DEVNULL, shell=True
        )


@fixture
async def app(docker) -> AsyncIterable[FastAPI]:
    async with LifespanManager(_app):
        yield _app


@fixture
async def client(app: FastAPI) -> AsyncIterable[AsyncClient]:
    async with AsyncClient(app=app, base_url='http://testserver') as client:
        yield client
