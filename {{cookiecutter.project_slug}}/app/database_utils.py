from unittest.mock import patch

from databases import Database
from loguru import logger
from sqlalchemy import create_engine

from . import config
from .models import metadata


def create_db():
    engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)
    metadata.create_all(engine, checkfirst=True)


async def populate_dev_db():
    from .models.user import get_all

    records = await get_all()
    if records:
        logger.debug('DEV/TEST database already populated')
        return

    logger.debug('Populating DEV/TEST database')
    async with Database(config.DATABASE_URL) as db:
        async with db.transaction():
            with patch('app.models.user.db', db):
                await populate_users()


async def populate_users() -> None:
    from .models.user import UserInsert, insert

    users = [
        UserInsert(
            name='Fulano de Tal',
            email='fulano@email.com',
            password='Paulo Paulada Power',
            is_admin=True,
        ),
        UserInsert(
            name='Beltrano de Tal',
            email='beltrano@email.com',
            password='abcdefgh1234567890',
            is_admin=False,
        ),
    ]

    for user in users:
        await insert(user)
