"""Pydantic schemas for working with Users"""

from pydantic import Field, BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    #is used for password and user data validation in Signup and Login endpoints
    username: str = Field(pattern=r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$', examples=["user@example.com"])
    password: str = Field(pattern=r'[a-zA-Z0-9&@%!$~#^*=]', examples=["string&123"])


class UserHashed(BaseModel):
    #is used for writing to the database
    email: str
    hashed_password: str

class JWT_dict(BaseModel):
    #the model for JWT token creation
    sub: str
    exp: datetime

class Token(BaseModel):
    #for successful response with token
    access_token: str
    token_type: str
    

class Message(BaseModel):
    detail: str
    
    


