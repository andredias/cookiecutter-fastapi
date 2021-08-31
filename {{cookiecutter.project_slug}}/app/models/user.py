from typing import Optional

import orjson as json
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, Integer, String, Table, Unicode

from .. import config
from ..resources import db, redis
from ..schemas.user import UserInfo, UserInsert, UserPatch
from . import metadata, random_id

crypt_ctx = CryptContext(schemes=['argon2'])


User = Table(
    'user',
    metadata,
    # Auto-incremented IDs are not particularly good for users as primary keys.
    # 1. Sequential IDs are guessable.
    #    One might guess that admin is always user with ID 1, for example.
    # 2. Tests end up using fixed ID values such as 1 or 2 instead of real values.
    #    This leads to poor test designs that should be avoided.
    Column('id', Integer, primary_key=True, autoincrement=False),
    Column('name', Unicode, nullable=False),
    Column('email', Unicode, nullable=False, unique=True),
    Column('password_hash', String(77), nullable=False),
    Column('is_admin', Boolean, default=False),
)


async def get_all() -> list[UserInfo]:
    query = User.select()
    logger.debug(query)
    result = await db.fetch_all(query)
    return [UserInfo(**r) for r in result]


async def get_user_by_email(email: str) -> Optional[UserInfo]:
    query = User.select(User.c.email == email)
    logger.debug(query)
    result = await db.fetch_one(query)
    return UserInfo(**result) if result else None


async def get_user_by_login(email: str, password: str) -> Optional[UserInfo]:
    query = User.select(User.c.email == email)
    logger.debug(query)
    result = await db.fetch_one(query)
    if result and crypt_ctx.verify(password, result['password_hash']):
        return UserInfo(**result)
    return None


async def get_user(id: int) -> Optional[UserInfo]:
    user_id = f'user:{id}'
    # search on Redis first
    result = await redis.get(user_id)
    if result:
        logger.debug(f'user {id} is cached')
        return UserInfo(**json.loads(result))

    # search in the database
    logger.debug(f'user {id} not cached')
    query = User.select(User.c.id == id)
    logger.debug(query)
    result = await db.fetch_one(query)
    if result:
        user = UserInfo(**result)
        # update Redis with the record
        await redis.set(user_id, user.json())
        await redis.expire(user_id, config.SESSION_LIFETIME)
        return user
    return None


async def insert(user: UserInsert) -> int:
    fields = user.dict()
    id_ = fields['id'] = random_id()
    password = fields.pop('password')
    fields['password_hash'] = crypt_ctx.hash(password)
    stmt = User.insert().values(fields)
    logger.debug(stmt)
    await db.execute(stmt)
    return id_


async def update(id: int, patch: UserPatch) -> None:
    fields = patch.dict(exclude_unset=True)
    if 'password' in fields:
        password = fields.pop('password')
        fields['password_hash'] = crypt_ctx.hash(password)
    stmt = User.update().where(User.c.id == id).values(**fields)
    logger.debug(stmt)
    await db.execute(stmt)
    await redis.delete(f'user:{id}')  # invalidate cache


async def delete(id: int) -> None:
    stmt = User.delete().where(User.c.id == id)
    logger.debug(stmt)
    await db.execute(stmt)
    await redis.delete(f'user:{id}')
