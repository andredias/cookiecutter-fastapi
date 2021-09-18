import asyncio
import sys
from string import ascii_uppercase

from aioredis import Redis
from databases import Database
from loguru import logger
from tenacity import RetryError, retry, stop_after_delay, wait_exponential

from . import config

db = Database(config.DATABASE_URL)
redis = Redis.from_url(config.REDIS_URL)


async def startup():
    setup_logger()
    show_config()
    await asyncio.gather(connect_redis(), connect_database())
    logger.info('started...')


async def shutdown():
    await db.disconnect()
    logger.info('...shutdown')


def setup_logger():
    """
    Configure Loguru's logger
    """
    _intercept_standard_logging_messages()
    logger.remove()  # remove standard handler
    logger.add(
        sys.stderr,
        level=config.LOG_LEVEL,
        colorize=True,
        backtrace=config.DEBUG,
        enqueue=True,
    )  # reinsert it to make it run in a different thread


def _intercept_standard_logging_messages():
    """
    Intercept standard logging messages toward loguru's logger
    ref: loguru README
    """
    import logging

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    logging.basicConfig(handlers=[InterceptHandler()], level=0)


def show_config() -> None:
    config_vars = {
        key: getattr(config, key)
        for key in sorted(dir(config))
        if key[0] in ascii_uppercase
    }
    logger.debug(config_vars)
    return


def create_db():
    from sqlalchemy import create_engine

    from .models import metadata

    engine = create_engine(config.DATABASE_URL, echo=config.TESTING)
    metadata.create_all(engine, checkfirst=True)


async def connect_database(database: Database = db) -> None:
    @retry(stop=stop_after_delay(3), wait=wait_exponential(multiplier=0.2))
    async def _connect_to_db() -> None:
        logger.debug('Connecting to the database...')
        await database.connect()

    try:
        await _connect_to_db()
        create_db()
        # migrate_db()
    except RetryError:
        logger.error('Could not connect to the database.')
        raise


async def connect_redis():

    # test redis connection
    @retry(stop=stop_after_delay(3), wait=wait_exponential(multiplier=0.2))
    async def _connect_to_redis() -> None:
        logger.debug('Connecting to Redis...')
        await redis.set('test_connection', '1234')
        await redis.delete('test_connection')

    try:
        await _connect_to_redis()
    except RetryError:
        logger.error('Could not connect to Redis')
        raise
    return
