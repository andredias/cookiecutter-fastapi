from asyncpg.exceptions import IntegrityConstraintViolationError
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from ..authentication import admin_user, authenticated_user, resource_owner
from ..models.user import delete, get_all, insert, update
from ..resources import db
from ..schemas import diff_models
from ..schemas.user import UserInfo, UserInsert, UserPatch

router = APIRouter()


@router.get('/users', response_model=list[UserInfo])
async def get_users(admin: UserInfo = Depends(admin_user)):
    return await get_all()


@router.get('/users/me', response_model=UserInfo)
async def get_self_info(user: UserInfo = Depends(authenticated_user)):
    return user


@router.get('/users/{id}', response_model=UserInfo)
async def get_user_info(id: int, user: UserInfo = Depends(resource_owner)):
    return user


@router.put('/users/{id}', status_code=204)
@db.transaction()
async def update_user(
    id: int,
    patch: UserPatch,
    user: UserInfo = Depends(resource_owner),
):
    fields = diff_models(user, patch)
    # temporary patch for issue #5
    # https://github.com/andredias/cookiecutter-fastapi/issues/5
    fields.pop('is_admin', None)
    try:
        await update(id, UserPatch(**fields))
    except IntegrityConstraintViolationError:
        logger.info(f'Integrity violation. {user} vs {patch}')
        raise HTTPException(422)
    return


@router.delete('/users/{id}', status_code=204)
@db.transaction()
async def delete_user(id: int, user: UserInfo = Depends(resource_owner)):
    await delete(id)


@router.post('/users', status_code=201)
@db.transaction()
async def create_user(user: UserInsert):
    # temporary patch for issue #5
    # https://github.com/andredias/cookiecutter-fastapi/issues/5
    user.is_admin = False
    try:
        id = await insert(user)
    except IntegrityConstraintViolationError:
        logger.info(f'Integrity violation. {user}')
        raise HTTPException(422)
    return {'id': id}
