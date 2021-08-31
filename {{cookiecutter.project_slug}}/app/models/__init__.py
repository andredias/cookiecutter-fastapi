from secrets import randbelow

from sqlalchemy import MetaData

metadata = MetaData()

MAX_ID = 2 ** 31


def random_id() -> int:
    return randbelow(MAX_ID)
