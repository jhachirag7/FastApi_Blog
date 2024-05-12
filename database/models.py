from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class Post(BaseModel):
    title: Optional[str]=None
    content:Optional[str]=None
    published: Optional[bool]=None

class Likes(BaseModel):
    post_id :str

