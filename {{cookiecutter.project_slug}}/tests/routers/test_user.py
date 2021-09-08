from httpx import AsyncClient

from app.models.user import UserInfo, UserInsert, get_user

from ..utils import logged_session

Users = list[UserInfo]


async def test_get_users(client: AsyncClient) -> None:
    resp = await client.get('/users')
    assert resp.status_code == 405


async def test_get_user(users: Users, client: AsyncClient) -> None:
    url = '/users/{}'

    # anonymous access to user account
    await logged_session(client)
    resp = await client.get(url.format(users[0].id))
    assert resp.status_code == 401

    # user tries to access his own info
    await logged_session(client, users[0].id)

    resp = await client.get(url.format(users[0].id))
    assert resp.status_code == 200
    assert UserInfo(**resp.json()) == users[0]

    # user tries to access another user info
    resp = await client.get(url.format(users[1].id))
    assert resp.status_code == 403

    # user tries to access inexistent user info')
    resp = await client.get(url.format(0))
    assert resp.status_code == 403


async def test_update_user(users: Users, client: AsyncClient) -> None:
    url = '/users/{}'
    email = 'fulano@pronus.io'
    name = 'Belafonte'

    # anonymous tries to update a user account
    resp = await client.put(url.format(users[0].id), json={'email': email})
    assert resp.status_code == 401

    # log as user 0
    await logged_session(client, users[0].id)

    # user tries to update another account
    resp = await client.put(url.format(users[1].id), json={'email': email})
    assert resp.status_code == 403

    # invalid password that doesn't satisfy the criteria
    resp = await client.put(
        url.format(users[0].id),
        json={'email': email, 'password': 'password123'},
    )
    assert resp.status_code == 422

    # user tries to update his own account
    resp = await client.put(
        url.format(users[0].id),
        json={'email': email, 'password': 'new password 123!'},
    )
    assert resp.status_code == 204
    user = await get_user(users[0].id)
    assert user and user.email == email

    # user tries to update his record using an existing email
    resp = await client.put(
        url.format(users[0].id), json={'email': users[1].email}
    )
    assert resp.status_code == 422

    # user tries to update inexistent user
    resp = await client.put(url.format(0), json={'name': name})
    assert resp.status_code == 403


async def test_delete_user(users: Users, client: AsyncClient) -> None:
    url = '/users/{}'

    # anonymous tries to delete a user account
    resp = await client.delete(url.format(users[0].id))
    assert resp.status_code == 401

    await logged_session(client, users[0].id)

    # user tries to delete another account
    resp = await client.delete(url.format(users[1].id))
    assert resp.status_code == 403

    # user tries to delete inexistent account
    resp = await client.delete(url.format(0))
    assert resp.status_code == 403

    # user tries to delete his own account
    resp = await client.delete(url.format(users[0].id))
    assert resp.status_code == 204
    assert await get_user(users[0].id) is None


async def test_create_user(client: AsyncClient) -> None:
    from faker import Faker

    fake = Faker()
    Faker.seed(0)
    user = UserInsert(
        name=fake.name(),
        email=fake.email(),
        password=fake.password(20),
        is_admin=fake.boolean(),
    )
    resp = await client.post('/users', content=user.json())
    assert resp.status_code == 405


async def test_get_me(users: Users, client: AsyncClient):
    await logged_session(client, users[0].id)
    resp = await client.get('/users/me')
    assert resp.status_code == 200
    assert UserInfo(**resp.json()) == users[0]
