from asyncpg.exceptions import IntegrityConstraintViolationError
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ..authentication import admin_user, authenticated_user
from ..models.user import delete, get_all, get_user, insert, update
from ..resources import db
from ..schemas import diff_models
from ..schemas.user import UserInfo, UserInsert, UserPatch

router = APIRouter()


async def selected_user(
    id: int,
    current_user: UserInfo = Depends(authenticated_user),
) -> UserInfo:
    if id != current_user.id and not current_user.is_admin:
        raise HTTPException(403)
    user = current_user if id == current_user.id else await get_user(id)
    if not user:
        raise HTTPException(404)
    return user


@router.get('/users', response_model=list[UserInfo])
async def get_users(admin: UserInfo = Depends(admin_user)):
    return await get_all()


@router.get('/users/{id}', response_model=UserInfo)
async def get_user_info(id: int, user: UserInfo = Depends(selected_user)):
    return user


@router.put('/users/{id}', status_code=204)
@db.transaction()
async def update_user(
    id: int,
    patch: UserPatch,
    user: UserInfo = Depends(selected_user),
):
    fields = diff_models(user, patch)
    try:
        await update(id, UserPatch(**fields))
    except IntegrityConstraintViolationError:
        logger.info(f'Integrity violation. {user} vs {patch}')
        raise HTTPException(422)
    return


@router.delete('/users/{id}', status_code=204)
@db.transaction()
async def delete_user(id: int, user: UserInfo = Depends(selected_user)):
    await delete(id)


@router.post('/users', status_code=201)
@db.transaction()
async def create_user(user: UserInsert):
    try:
        id = await insert(user)
    except IntegrityConstraintViolationError:
        logger.info(f'Integrity violation. {user}')
        raise HTTPException(422)
    return {'id': id}
