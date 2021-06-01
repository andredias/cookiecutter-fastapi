from typing import Optional

from loguru import logger
from sqlalchemy import Column, Date, String, Table, Unicode

from ..resources import db
from ..schemas.user import User as UserSchema
from ..schemas.user import UserIn
from . import metadata

User = Table(
    'user',
    metadata,
    Column('cpf', String(11), primary_key=True, autoincrement=False),
    Column('nome', Unicode, nullable=False),
    Column('nascimento', Date, nullable=False),
    Column('logradouro', Unicode, nullable=False),
    Column('bairro', Unicode, nullable=False),
    Column('cidade', Unicode, nullable=False),
    Column('uf', String(2), nullable=False),
    Column('cep', String(8), nullable=False),
)


async def get_all() -> list[UserSchema]:
    query = User.select()
    logger.debug(query)
    result = await db.fetch_all(query)
    return [UserSchema(**r) for r in result]


async def get_user(cpf: str) -> Optional[UserSchema]:
    query = User.select(User.c.cpf == cpf)
    logger.debug(query)
    result = await db.fetch_one(query)
    if result:
        user = UserSchema(**result)
        return user
    return None


async def insert(user: UserSchema) -> None:
    query = User.insert().values(**user.dict())
    logger.debug(query)
    await db.execute(query)
    return


async def update(user: UserIn) -> None:
    cpf = user.cpf
    fields = user.dict(exclude={'cpf'}, exclude_unset=True)
    query = User.update().where(User.c.cpf == cpf).values(**fields)
    logger.debug(query)
    await db.execute(query)


async def delete(cpf: str) -> None:
    query = User.delete().where(User.c.cpf == cpf)
    logger.debug(query)
    await db.execute(query)
