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
async def populate_test_db() -> None:
    """
    Populate database with test data.
    """
    await populate_db()


@fixture
async def app(populate_test_db: None) -> AsyncIterable[FastAPI]:
    """
    Create a FastAPI instance.

    1. Populate database with test data only once
    2. Create a FastAPI instance
    3. Execute lifespan cycle
    4. Create a global transaction to wrap each test.

       * DBTransactionMiddleware only wraps each REST API endpoint,
         but not the test itself.
       * The global force_rollback provided by Encode/Databases doesn't play well
         with inner transactions and cause issues.
    """
    async with LifespanManager(_app):
        async with db.connection() as conn:
            async with conn.transaction(force_rollback=True):
                yield _app


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
