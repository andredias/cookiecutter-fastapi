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


@fixture
async def app() -> AsyncIterable[FastAPI]:
    async with LifespanManager(_app):
        async with db.transaction(force_rollback=True):  # global rollback
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
