"""The file for Posts' pydantic models """

from pydantic import BaseModel, EmailStr, UUID4, Field
from datetime import datetime


class PostCreate(BaseModel):
    #enter model for AddPost endpoint
    Post_Text: str = Field(min_length=1)
    

class PostDelete(BaseModel):
    #enter model for DeletePost endpoint
    Post_ID: UUID4

class PostAddGet(BaseModel):
    #the model for adding data to the database
    Post_ID: UUID4
    Post_Text: str
    User_Email: EmailStr
    Creation_DateTime: datetime

class PostOut(BaseModel):
    #the response of AddPost endpoint
    Post_ID: UUID4

class Message(BaseModel):
    detail: str