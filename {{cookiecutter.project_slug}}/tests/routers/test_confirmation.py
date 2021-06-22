from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from loguru import logger

from app.models.user import UserInfo, UserInsert, get_user_by_login
from app.sessions import create_session, delete_session, session_exists

Users = list[UserInfo]


@patch('app.routers.confirmation.create_session')
async def test_send_reset_password_instructions(
    create_session: AsyncMock, users: Users, client: AsyncClient
) -> None:
    logger.info('invalid email')
    email = 'teste123email.com'
    resp = await client.get(
        '/send_reset_password_instructions', params={'email': email}
    )
    assert resp.status_code == 422

    logger.info('valid but non-existing email')
    email = 'teste@email.com'
    resp = await client.get(
        '/send_reset_password_instructions', params={'email': email}
    )
    assert resp.status_code == 200
    create_session.assert_not_awaited()

    logger.info('valid existing email')
    resp = await client.get(
        '/send_reset_password_instructions', params={'email': users[1].email}
    )
    assert resp.status_code == 200
    create_session.assert_awaited()


async def test_reset_password(users: Users, client: AsyncClient) -> None:
    old_password = 'abcdefgh1234567890'

    logger.info('session without payload')
    session_id = await create_session(users[1].email)
    resp = await client.post(
        '/reset_password',
        json=dict(session_id=session_id, password='new password!!!'),
    )
    assert resp.status_code == 500
    await delete_session(session_id)

    logger.info('expired session')
    session_id = await create_session(users[1].email, str(users[1].id), 1)
    await delete_session(session_id)
    resp = await client.post(
        '/reset_password',
        json=dict(session_id=session_id, password='new password!!!'),
    )
    assert resp.status_code == 404

    session_id = await create_session(users[1].email, str(users[1].id), 3600)

    logger.info('invalid password')
    resp = await client.post(
        '/reset_password',
        json=dict(session_id=session_id, password='new password'),
    )
    assert resp.status_code == 422

    logger.info('ok')
    assert await get_user_by_login(email=users[1].email, password=old_password)
    password = 'new password!!!'
    resp = await client.post(
        '/reset_password',
        json=dict(session_id=session_id, password=password),
    )
    assert resp.status_code == 200
    user = await get_user_by_login(email=users[1].email, password=old_password)
    assert user is None
    user = await get_user_by_login(email=users[1].email, password=password)
    assert user and user.id == users[1].id
    assert (await session_exists(session_id)) is False


@patch('app.routers.confirmation.create_session')
async def test_send_register_user_instructions(
    create_session: AsyncMock, users: Users, client: AsyncClient
) -> None:
    logger.info('invalid email')
    email = 'teste123email.com'
    resp = await client.get(
        '/send_register_user_instructions', params={'email': email}
    )
    assert resp.status_code == 422

    logger.info('valid but email already exists')
    resp = await client.get(
        '/send_register_user_instructions', params={'email': users[1].email}
    )
    assert resp.status_code == 200
    create_session.assert_not_awaited()

    logger.info('valid non-existing email')
    email = 'teste@email.com'
    resp = await client.get(
        '/send_register_user_instructions', params={'email': email}
    )
    assert resp.status_code == 200
    create_session.assert_awaited()


async def test_register_user(users: Users, client: AsyncClient) -> None:
    user = UserInsert(
        name='Sicrano', email='sicrano@email.com', password='abcdefgh1234567890'
    )
    session_id = await create_session(user.email, lifetime=3600)
    await delete_session(session_id)

    logger.info('invalid session')
    resp = await client.post(
        '/register_user',
        json=dict(session_id=session_id, user=user.dict()),
    )
    assert resp.status_code == 404

    session_id = await create_session(user.email, lifetime=3600)

    logger.info('different session and user email')
    user2 = UserInsert(
        name='Sicrano', email='teste@email.com', password='abcdefgh1234567890'
    )
    resp = await client.post(
        '/register_user',
        json=dict(session_id=session_id, user=user2.dict()),
    )
    assert resp.status_code == 422

    logger.info('ok')
    resp = await client.post(
        '/register_user',
        json=dict(session_id=session_id, user=user.dict()),
    )
    assert resp.status_code == 201

    assert await get_user_by_login(email=user.email, password=user.password)
    assert (await session_exists(session_id)) is False
