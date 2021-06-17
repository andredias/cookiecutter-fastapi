import sys
from string import ascii_uppercase

from aioredis import Redis
from databases import Database
from loguru import logger
from tenacity import RetryError, retry, stop_after_delay, wait_exponential

from . import config
from .utils import populate_dev_db

db = Database(config.DATABASE_URL, force_rollback=config.TESTING)
redis = Redis.from_url(config.REDIS_URL)


async def startup():
    setup_logger()
    if config.DEBUG:
        show_config()
    await _init_redis()
    await _init_database()
    if config.DEBUG:
        await populate_dev_db()
    logger.info('started...')


async def shutdown():
    await _stop_database()
    await _stop_redis()
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


async def _init_redis():

    # test redis connection
    @retry(stop=stop_after_delay(3), wait=wait_exponential(multiplier=0.2))
    async def _connect_to_redis() -> None:
        logger.debug('Connecting to Redis...')
        await redis.set('test_connection', '1234')
        await redis.delete('test_connection')

    await _connect_to_redis()
    return


async def _stop_redis():
    if config.TESTING:
        await redis.flushdb()
