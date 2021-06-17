async def populate_dev_db():
    from .models.user import UserInsert, insert

    users = [
        dict(
            name='Fulano de Tal',
            email='fulano@email.com',
            password='Paulo Paulada Power',
            is_admin=True,
        ),
        dict(
            name='Beltrano de Tal',
            email='beltrano@email.com',
            password='abcd1234',
            is_admin=False,
        ),
    ]
    for user in users:
        await insert(UserInsert(**user))
