from httpx import AsyncClient
from loguru import logger

from app.models.user import UserInfo, UserInsert, get_user, insert

from ..utils import logged_session

Users = list[UserInfo]


async def test_get_users(users: Users, client: AsyncClient) -> None:
    admin_id = users[0].id
    user_id = users[1].id
    url = '/users'

    await logged_session(client, admin_id)
    resp = await client.get(url)
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    await logged_session(client, user_id)
    resp = await client.get(url)
    assert resp.status_code == 403

    await logged_session(client)
    resp = await client.get(url)
    assert resp.status_code == 401


async def test_get_user(users: Users, client: AsyncClient) -> None:
    admin_id = users[0].id
    user_id = users[1].id
    url = '/users/{}'

    logger.info('normal user try to access its own info')
    await logged_session(client, user_id)
    resp = await client.get(url.format(user_id))
    assert resp.status_code == 200
    assert UserInfo(**resp.json()) == users[1]

    logger.info('normal user try to access another user info')
    resp = await client.get(url.format(admin_id))
    assert resp.status_code == 403

    logger.info('admin access to another user info')
    await logged_session(client, admin_id)
    resp = await client.get(url.format(user_id))
    assert resp.status_code == 200
    assert UserInfo(**resp.json()) == users[1]

    logger.info('admin access to inexistent user')
    resp = await client.get(url.format(user_id + 1))
    assert resp.status_code == 404

    logger.info('anonymous access to user account')
    await logged_session(client)
    resp = await client.get(url.format(user_id))
    assert resp.status_code == 401


async def test_update_user(users: Users, client: AsyncClient) -> None:
    admin_id = users[0].id
    user_id = users[1].id
    url = '/users/{}'
    email = 'beltrano@pronus.io'
    name = 'Belafonte'

    logger.info('anonymous tries to update a user account')
    resp = await client.put(url.format(user_id), json={'email': email})
    assert resp.status_code == 401

    logger.info('normal user tries to update another account')
    await logged_session(client, user_id)
    resp = await client.put(url.format(admin_id), json={'email': email})
    assert resp.status_code == 403

    logger.info('normal user tries to update his own account')
    resp = await client.put(
        url.format(user_id), json={'email': email, 'password': 'password123'}
    )
    assert resp.status_code == 204
    user = await get_user(user_id)
    assert user and user.email == email

    logger.info('normal user tries to update existing email')
    resp = await client.put(url.format(user_id), json={'email': users[0].email})
    assert resp.status_code == 422

    logger.info('admin updates a user')
    await logged_session(client, admin_id)
    resp = await client.put(
        url.format(user_id), json={'name': name, 'is_admin': True}
    )
    assert resp.status_code == 204
    user = await get_user(user_id)
    assert user and user.name == name and user.is_admin is False

    logger.info('admin tries to update inexistent user')
    resp = await client.put(url.format(user_id + 1), json={'name': name})
    assert resp.status_code == 404


async def test_delete_user(users: Users, client: AsyncClient) -> None:
    admin_id = users[0].id
    user_id = users[1].id
    third_id = await insert(
        UserInsert(
            name='Sicrano',
            email='sicrano@email.com',
            password='Sicrano Tralalá',
        )
    )
    url = '/users/{}'

    logger.info('anonymous tries to delete a user account')
    resp = await client.delete(url.format(user_id))
    assert resp.status_code == 401

    logger.info('sicrano tries to delete another account')
    await logged_session(client, third_id)
    resp = await client.delete(url.format(admin_id))
    assert resp.status_code == 403

    logger.info('sicrano tries to delete his own account')
    resp = await client.delete(url.format(third_id))
    assert resp.status_code == 204
    assert await get_user(third_id) is None

    logger.info('admin deletes a user')
    await logged_session(client, admin_id)
    resp = await client.delete(url.format(user_id))
    assert resp.status_code == 204

    logger.info('admin tries to delete inexistent user')
    resp = await client.delete(url.format(user_id + 1))
    assert resp.status_code == 404


async def test_create_user(users: Users, client: AsyncClient) -> None:
    from faker import Faker

    fake = Faker()
    Faker.seed(0)

    def fake_user() -> UserInsert:
        return UserInsert(
            name=fake.name(),
            email=fake.email(),
            password=fake.password(20),
            is_admin=True,
        )

    admin_id = users[0].id
    user_id = users[1].id

    logger.info('anonymous tries to create a user account')
    user = fake_user()
    resp = await client.post('/users', content=user.json())
    assert resp.status_code == 201
    id = resp.json()['id']
    user_info = UserInfo(**user.dict(exclude={'is_admin'}), id=id, is_admin=False)
    assert (await get_user(id)) == user_info

    logger.info('anonymous tries to recreate an existing user account')
    resp = await client.post('/users', content=user.json())
    assert resp.status_code == 422

    logger.info('user tries to create another account')
    user = fake_user()
    await logged_session(client, user_id)
    resp = await client.post('/users', content=user.json())
    id = resp.json()['id']
    assert resp.status_code == 201
    user_info = UserInfo(**user.dict(exclude={'is_admin'}), id=id, is_admin=False)
    assert (await get_user(id)) == user_info

    logger.info('admin tries to create another account')
    user = fake_user()
    await logged_session(client, admin_id)
    resp = await client.post('/users', content=user.json())
    assert resp.status_code == 201
    id = resp.json()['id']
    user_info = UserInfo(**user.dict(exclude={'is_admin'}), id=id, is_admin=False)
    assert (await get_user(id)) == user_info


async def test_get_me(users: Users, client: AsyncClient):
    user_id = users[1].id
    await logged_session(client, user_id)
    resp = await client.get('/users/me')
    assert resp.status_code == 200
    assert UserInfo(**resp.json()) == users[1]
