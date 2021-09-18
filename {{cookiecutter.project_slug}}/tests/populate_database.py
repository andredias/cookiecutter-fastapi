from loguru import logger


async def populate_db():
    from app.models.user import get_all

    records = await get_all()
    if records:
        logger.debug('DEV/TEST database already populated')
        return

    logger.debug('Populating DEV/TEST database')
    await populate_users()


async def populate_users() -> None:
    from app.models.user import UserInsert, insert

    users = [
        UserInsert(
            name='Fulano de Tal',
            email='fulano@email.com',
            password='Paulo Paulada Power',
        ),
        UserInsert(
            name='Beltrano de Tal',
            email='beltrano@email.com',
            password='abcdefgh1234567890',
        ),
    ]

    for user in users:
        await insert(user)
