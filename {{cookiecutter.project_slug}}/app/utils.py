async def populate_dev_db():
    from .models.user import UserInsert, get_all, insert

    records = await get_all()
    if records:
        return

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
            password='abcdefgh1234567890',
            is_admin=False,
        ),
    ]
    for user in users:
        await insert(UserInsert(**user))
