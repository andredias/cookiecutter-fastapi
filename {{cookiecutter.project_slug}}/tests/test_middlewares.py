from unittest.mock import patch

from asyncpg.exceptions import InFailedSQLTransactionError, UniqueViolationError
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient
from pytest import raises

from app.models.user import UserInfo, UserInsert, delete, get_user, insert
from app.resources import db

Users = list[UserInfo]


async def test_dbtransactionwrappermiddleware(
    app: FastAPI, client: AsyncClient, users: Users, connection
):
    async def dispatch(request, call_next):
        return await call_next(request)

    @app.post('/test_db_transaction_wrapper')
    async def dbtransactionwrappermiddleware():
        try:
            await delete(users[1].id)
            # should raise an exception due to email duplication
            await insert(
                UserInsert(password='abcdefgh1234!.=>', **users[0].dict())
            )
        except UniqueViolationError:
            pass  # leaves the transaction in a inconsistent state
        raise HTTPException(422)

    # middleware disabled
    with raises(InFailedSQLTransactionError):
        async with db.transaction(force_rollback=True):
            with patch('app.middlewares._dispatch', side_effect=dispatch):
                response = await client.post('/test_db_transaction_wrapper')
            assert response.status_code == 422
            await get_user(users[1].id)

    # middleware enabled
    response = await client.post('/test_db_transaction_wrapper')
    assert response.status_code == 422
    assert await get_user(users[1].id) == users[1]
