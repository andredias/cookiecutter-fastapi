import sys
from string import ascii_uppercase

from databases import Database
from loguru import logger
from tenacity import RetryError, retry, stop_after_delay, wait_exponential

from . import config

db = Database(config.DATABASE_URL, force_rollback=config.TESTING)


async def startup():
    setup_logger()
    if config.DEBUG:
        show_config()
    await _init_database()
    logger.info('started...')


async def shutdown():
    await _stop_database()
    logger.info('...shutdown')


def setup_logger():
    """
    Configure Loguru's logger
    """
    logger.remove()  # remove standard handler
    logger.add(
        sys.stderr,
        level=config.LOG_LEVEL,
        colorize=True,
        backtrace=config.DEBUG,
        enqueue=True,
    )  # reinsert it to make it run in a different thread


def show_config() -> None:
    values = {
        v: getattr(config, v)
        for v in sorted(dir(config))
        if v[0] in ascii_uppercase
    }
    logger.debug(values)
    return


async def _init_database() -> None:
    from sqlalchemy import create_engine

    from .models import metadata

    @retry(stop=stop_after_delay(3), wait=wait_exponential(multiplier=0.2))
    async def _connect_to_db() -> None:
        logger.debug('Connecting to database...')
        await db.connect()

    try:
        await _connect_to_db()
    except RetryError:
        logger.error('Não foi possível conectar ao banco de dados.')
        raise
    engine = create_engine(config.DATABASE_URL)
    metadata.create_all(engine, checkfirst=True)


async def _stop_database() -> None:
    await db.disconnect()
