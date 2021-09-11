from unittest.mock import patch

from fastapi import FastAPI, HTTPException
from httpx import AsyncClient

from app.models.user import UserInfo, delete, get_user
from app.resources import db

Users = list[UserInfo]


async def test_dbtransactionwrappermiddleware(
    app: FastAPI, client: AsyncClient, users: Users
):
    async def dispatch(request, call_next):
        return await call_next(request)

    @app.delete('/db_transaction_1')
    async def dbtransactionwrappermiddleware():
        await delete(users[0].id)
        raise HTTPException(500)

    # middleware disabled
    async with db.transaction(force_rollback=True):
        with patch('app.middlewares._dispatch', side_effect=dispatch):
            response = await client.delete('/db_transaction_1')
        assert response.status_code == 500
        assert await get_user(users[0].id) is None

    assert await get_user(users[0].id) is not None

    # middleware enabled
    async with db.transaction(force_rollback=True):
        with patch('app.middlewares.TESTING', False):
            response = await client.delete('/db_transaction_1')
        assert response.status_code == 500
        assert await get_user(users[0].id) == users[0]
