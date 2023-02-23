import datetime as _dt

from pydantic import BaseModel


class _PostBase(BaseModel):
    title: str
    content: str


class PostCreate(_PostBase):
    ...


class Post(_PostBase):
    id: int
    owner_id: int
    title: str
    content: str
    data_created: _dt.datetime
    date_last_updated: _dt.datetime

    class Config:
        orm_mode = True


class _UserBase(BaseModel):
    email: str


class UserCreate(_UserBase):
    password: str


class Source(_UserBase):
    id: int
    is_active: bool
    posts: list[Post] = []

    class Config:
        orm_mode = True
