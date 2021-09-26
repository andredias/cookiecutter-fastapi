from unittest.mock import patch

from databases import Database
from loguru import logger

from app import config
from app.resources import connect_database, create_db

test_db = Database(config.DATABASE_URL)


@patch('app.models.user.db', test_db)
async def populate_db():
    from app.models.user import get_all

    await connect_database(test_db)
    create_db()

    records = await get_all()
    if records:
        logger.debug('DEV/TEST database already populated')
        return

    logger.debug('Populating DEV/TEST database')
    try:
        await populate_users()
        # include new populate methods here
    finally:
        await test_db.disconnect()


@patch('app.models.user.db', test_db)
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
