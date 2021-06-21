from asyncpg.exceptions import IntegrityConstraintViolationError
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ..authentication import admin_user, authenticated_user, owner_or_admin
from ..models.user import delete, get_all, get_user, insert, update
from ..resources import db, redis
from ..schemas import diff_models
from ..schemas.user import UserInfo, UserInsert, UserPatch

router = APIRouter()


async def target_user(id: int, current_user: UserInfo) -> UserInfo:
    user = current_user if id == current_user.id else await get_user(id)
    if not user:
        raise HTTPException(404)
    return user


@router.get('/users', response_model=list[UserInfo])
async def get_users(admin: UserInfo = Depends(admin_user)):
    return await get_all()


@router.get('/users/me', response_model=UserInfo)
async def get_self_info(user: UserInfo = Depends(authenticated_user)):
    return user


@router.get('/users/{id}', response_model=UserInfo)
async def get_user_info(
    id: int, current_user: UserInfo = Depends(owner_or_admin)
):
    user = await target_user(id, current_user)
    return user


@router.put('/users/{id}', status_code=204)
@db.transaction()
async def update_user(
    id: int,
    patch: UserPatch,
    current_user: UserInfo = Depends(owner_or_admin),
):
    if 'is_admin' in patch.dict(exclude_unset=True) and not current_user.is_admin:
        raise HTTPException(403)

    user = await target_user(id, current_user)
    patch = UserPatch(**diff_models(user, patch))
    try:
        await update(id, patch)
    except IntegrityConstraintViolationError:
        logger.info(f'Integrity violation in {user} vs {patch}')
        raise HTTPException(422)
    return


@router.delete('/users/{id}', status_code=204)
@db.transaction()
async def delete_user(id: int, current_user: UserInfo = Depends(owner_or_admin)):
    await target_user(id, current_user)
    await delete(id)
    sessions = await redis.keys(f'user:{id}*')
    if sessions:
        await redis.delete(*sessions)


@router.post('/users', status_code=201, response_model=UserInfo)
@db.transaction()
async def create_user(user: UserInsert, admin: UserInfo = Depends(admin_user)):
    try:
        id = await insert(user)
    except IntegrityConstraintViolationError:
        logger.info(f'Integrity violation. {user}')
        raise HTTPException(422)
    return await get_user(id)
