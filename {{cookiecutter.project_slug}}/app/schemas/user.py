from typing import Optional

from pydantic import BaseModel, EmailStr


class UserInfo(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool = False


class UserInsert(BaseModel):
    name: str
    email: EmailStr
    password: str
    is_admin: bool = False


class UserPatch(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    is_admin: Optional[bool] = False
