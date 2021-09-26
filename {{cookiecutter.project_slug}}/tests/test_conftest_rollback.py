"""
There is still a bug in pytest-asyncio/alt-pytest-asyncio that prevents
the context to be properly used in each test.
This makes the global transaction not to work properly.

See:

    * https://www.linw1995.com/en/blog/How-To-Write-Asynchronous-Code-With-Contextvars-Properly/  # noqa: E501
    * https://github.com/pytest-dev/pytest-asyncio/pull/161

The tests in this file detect that bug.
"""

import pytest

from app.models.user import delete, get_all
from app.resources import db


@pytest.mark.skip(reason='contextvar propagation to fixture is not solved yet')
async def test_rollback_delete_user(app):
    users = await get_all()
    async with db.connection() as conn:
        async with conn.transaction(force_rollback=True):
            await delete(users[0].id)
    assert len(await get_all()) == 2


@pytest.mark.skip(reason='contextvar propagation to fixture is not solved yet')
async def test_delete_user_1(users, client):
    await delete(users[0].id)


@pytest.mark.skip(reason='contextvar propagation to fixture is not solved yet')
async def test_delete_user_2(users, client):
    assert len(users) == 2
