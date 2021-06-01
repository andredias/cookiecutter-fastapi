from fastapi import APIRouter, HTTPException
from loguru import logger

from ..models.user import delete, get_all, get_user, insert, update
from ..schemas.user import User, UserIn

router = APIRouter()


@router.get('/users', response_model=list[User])
async def get_users():
    result = await get_all()
    logger.debug(result)
    return result


@router.get('/users/{cpf}', response_model=User)
async def get_one_user(cpf: str):
    user = await get_user(cpf)
    if not user:
        raise HTTPException(404)
    return user


@router.post('/users', status_code=201)
async def include_user(user: User):
    logger.debug(user)
    await insert(user)
    return


@router.put('/users', status_code=204)
async def update_user(user: UserIn):
    logger.debug(user)
    old_user = await get_user(user.cpf)
    if not old_user:
        raise HTTPException(404)
    await update(user)
    return


@router.delete('/users/{cpf}', status_code=204)
async def delete_user(cpf: str):
    user = await get_user(cpf)
    if not user:
        raise HTTPException(404)
    await delete(cpf)
    return
