from unittest.mock import AsyncMock, patch

from loguru import logger

from app.sessions import (  # isort:skip
    create_csrf,
    create_session,
    delete_session,
    get_session,
    is_valid_csrf,
    session_exists,
)


async def test_session(app) -> None:
    data = {'user_id': 1}

    logger.info('create session')
    session_id = await create_session(data)
    assert session_id
    assert await session_exists(session_id)

    logger.info('get_session')
    resp_data = await get_session(session_id)
    assert resp_data == data

    logger.info('delete_session')
    await delete_session(session_id)
    resp_data = await get_session(session_id)
    assert resp_data is None
    assert not await session_exists(session_id)


async def test_create_csrf(app) -> None:
    session_id = await create_session({'user_id': 12345})
    csrf = create_csrf(session_id)
    assert is_valid_csrf(session_id, csrf)


@patch('app.sessions.redis', new_callable=AsyncMock)
async def test_renew_session(redis: AsyncMock, app) -> None:
    data = {'user_id': 1}
    session_id = await create_session(data)
    redis.get.return_value = '{"user_id": 1}'
    _ = await get_session(session_id)
    assert redis.expire.call_count == 1
