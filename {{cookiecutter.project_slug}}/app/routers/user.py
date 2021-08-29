from asyncpg.exceptions import IntegrityConstraintViolationError
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ..authentication import admin_user, authenticated_user, owner_or_admin
from ..models.user import delete, get_all, get_user, insert, update
from ..resources import db, redis
from ..schemas import diff_models
from ..schemas.user import UserInfo, UserInsert, UserPatch

router = APIRouter(prefix='/users', tags=['users'])


async def target_user(
    id: int, current_user: UserInfo = Depends(owner_or_admin)
) -> UserInfo:
    user = current_user if id == current_user.id else await get_user(id)
    if not user:
        raise HTTPException(404)
    return user


@router.get('', response_model=list[UserInfo], dependencies=[Depends(admin_user)])
async def get_users():
    return await get_all()


@router.get('/me', response_model=UserInfo)
async def get_self_info(user: UserInfo = Depends(authenticated_user)):
    return user


@router.get('/{id}', response_model=UserInfo)
async def get_user_info(id: int, user: UserInfo = Depends(target_user)):
    return user


@router.put('/{id}', status_code=204)
@db.transaction()
async def update_user(
    id: int,
    patch: UserPatch,
    current_user: UserInfo = Depends(owner_or_admin),
    user: UserInfo = Depends(target_user),
):
    if 'is_admin' in patch.dict(exclude_unset=True) and not current_user.is_admin:
        raise HTTPException(403)
    patch = UserPatch(**diff_models(user, patch))
    try:
        await update(id, patch)
    except IntegrityConstraintViolationError:
        logger.info(f'Integrity violation in {user} vs {patch}')
        raise HTTPException(422)
    return


@router.delete('/{id}', status_code=204, dependencies=[Depends(target_user)])
@db.transaction()
async def delete_user(id: int):
    await delete(id)
    sessions = await redis.keys(f'user:{id}*')
    if sessions:
        await redis.delete(*sessions)


@router.post(
    '',
    status_code=201,
    response_model=UserInfo,
    dependencies=[Depends(admin_user)],
)
@db.transaction()
async def create_user(user: UserInsert):
    try:
        id = await insert(user)
    except IntegrityConstraintViolationError:
        logger.info(f'Integrity violation. {user}')
        raise HTTPException(422)
    return await get_user(id)
