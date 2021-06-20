import json
from unittest.mock import AsyncMock, patch

from loguru import logger
from pytest import mark

from app.sessions import (
    create_csrf,
    create_session,
    delete_session,
    get_session_payload,
    is_valid_csrf,
    session_exists,
)


async def test_session(app) -> None:
    data = {'user_id': 1}

    logger.info('create session')
    session_id = await create_session('user:1', json.dumps(data))
    assert session_id
    assert await session_exists(session_id)

    logger.info('get_session')
    resp_data = await get_session_payload(session_id)
    assert resp_data and json.loads(resp_data) == data

    logger.info('delete_session')
    await delete_session(session_id)
    resp_data = await get_session_payload(session_id)
    assert resp_data is None
    assert not await session_exists(session_id)


async def test_create_csrf(app) -> None:
    session_id = await create_session('user:12345')
    csrf = create_csrf(session_id)
    assert is_valid_csrf(session_id, csrf)


@mark.skip('no way to renew session for now')
@patch('app.sessions.redis', new_callable=AsyncMock)
async def test_renew_session(redis: AsyncMock, app) -> None:
    session_id = await create_session('user:1')
    redis.get.return_value = '{"user_id": 1}'
    _ = await get_session_payload(session_id)
    assert redis.expire.call_count == 1
