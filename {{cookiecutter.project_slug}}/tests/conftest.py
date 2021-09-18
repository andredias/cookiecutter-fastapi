"""
Important
---------

Tests will only work if service containers are running.
See Makefile for instructions.
"""

from typing import AsyncIterable

from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from pytest import fixture

from app.main import app as _app
from app.models.user import get_all as get_all_users
from app.resources import db
from app.schemas.user import UserInfo

from .populate_database import populate_db


@fixture(scope='session')
async def basic_app() -> AsyncIterable[FastAPI]:
    """
    Lifespan, showing config and populate test database
    are once-time events.
    """
    async with LifespanManager(_app):
        await populate_db()
        yield _app


@fixture
async def redis(basic_app):
    """
    Empty redis after each test
    """

    from app.resources import redis as _redis

    try:
        yield
    finally:
        await _redis.flushdb()


@fixture
async def app(basic_app, redis) -> AsyncIterable[FastAPI]:
    """
    Global transaction that wraps all others and roll back all changes after
    each test.
    """
    async with db.transaction(force_rollback=True):  # global rollback
        yield basic_app


@fixture
async def client(app: FastAPI) -> AsyncIterable[AsyncClient]:
    async with AsyncClient(
        app=app,
        base_url='http://testserver',
        headers={'Content-Type': 'application/json'},
    ) as client:
        yield client


@fixture
async def users(app) -> list[UserInfo]:
    """
    Users were already created at app.utils.populate_dev_db
    during app startup event.
    """
    return await get_all_users()
