from asyncpg.exceptions import IntegrityConstraintViolationError
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ..authentication import authenticated_user
from ..models.user import delete, update
from ..resources import db, redis
from ..schemas import diff_models
from ..schemas.user import UserInfo, UserPatch

router = APIRouter(prefix='/users', tags=['users'])


async def self_user(
    id: int,
    current_user: UserInfo = Depends(authenticated_user),
) -> UserInfo:
    if id == current_user.id:
        return current_user
    raise HTTPException(403)


@router.get('', status_code=405)
async def get_all():
    return


@router.get('/me', response_model=UserInfo)
async def get_self_info(user: UserInfo = Depends(authenticated_user)):
    return user


@router.get('/{id}', response_model=UserInfo)
async def get_user_info(id: int, user: UserInfo = Depends(self_user)):
    return user


@router.put('/{id}', status_code=204)
@db.transaction()
async def update_user(
    id: int,
    patch: UserPatch,
    user: UserInfo = Depends(self_user),
):
    patch = UserPatch(**diff_models(user, patch))
    try:
        await update(id, patch)
    except IntegrityConstraintViolationError:
        logger.info(f'Integrity violation in {user} vs {patch}')
        raise HTTPException(422)
    return


@router.delete('/{id}', status_code=204, dependencies=[Depends(self_user)])
@db.transaction()
async def delete_user(id: int):
    await delete(id)
    sessions = await redis.keys(f'user:{id}*')
    if sessions:
        await redis.delete(*sessions)
    return
