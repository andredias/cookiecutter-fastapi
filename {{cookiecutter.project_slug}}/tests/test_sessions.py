import json

from loguru import logger

from app.sessions import (
    create_csrf,
    create_session,
    delete_session,
    get_session_payload,
    is_valid_csrf,
    session_exists,
    session_keys,
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


async def test_session_keys(app):
    sessions = [
        await create_session('test@email.com'),
        await create_session('user:1234'),
        await create_session('user:23455'),
    ]

    keys = await session_keys('user:*')
    assert len(keys) == 2
    assert sessions[0] not in keys
