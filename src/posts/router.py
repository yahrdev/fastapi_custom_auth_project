"""The file with Posts enpoints"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import delete, insert, select
from posts.models import Post
from fastapi import Depends, Query
from database import get_session
from posts.schemas import PostCreate, PostDelete, PostAddGet, PostOut, Message
from auth.auth_base import verify_token, oauth2_scheme
from datetime import datetime, timezone
from cachetools import TTLCache
from uuid import uuid4
from typing import Annotated, Any
from fastapi.responses import JSONResponse
from logging import error
from inspect import currentframe

#current_func is the name of the current function. Just for understandable error

router_posts = APIRouter(
    prefix="/posts",
    tags=["Posts"], 
    responses={500: {"model": Message},
               401: {"model": Message},
               498: {"model": Message}})

SessionDep = Annotated[Any, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme), Query(description="Current user token")]



def handle_server_error(exception: Exception):
    #general function for general 500 error
    error(exception)
    raise HTTPException(status_code=500, detail="Internal Server Error")



@router_posts.get("/GetPosts", response_model=list[PostAddGet])
def get_posts(token: TokenDep,
                    session: SessionDep) -> Any:  
    """
    Get the posts with the following information:

    - **Post_ID**: GUID, is generated automatically
    - **User_Email**: email
    - **Post_Text**: can not be bigger then 1MB
    - **Creation_DateTime**: is generated automatically
    """
    current_func = currentframe().f_code.co_name
    useremail = verify_token(token, session)
    try:
        if useremail:
            """we find data in the cash. If it does not exist or empty, we update it"""
            found_posts = _get_cached_posts(useremail)
            if not found_posts:
                found_posts = _get_posts(useremail, session)
                _update_cached_posts(useremail, found_posts, clear = False)
            return found_posts
    except Exception as e:
            handle_server_error(f"{current_func} error: {e}")



@router_posts.post("/AddPost", response_model=PostOut, responses = {413: {"model": Message}})
def add_post(newpostinf: PostCreate, session: SessionDep, 
             token: TokenDep) -> Any:
    """
    Create a post with the following information:

    - **Post_ID**: GUID, is generated automatically
    - **User_Email**: email
    - **Post_Text**: can not be bigger then 1MB
    - **Creation_DateTime**: is generated automatically
    """
    current_func = currentframe().f_code.co_name
    useremail = verify_token(token, session)
    if useremail:
        try:
            """we create a model of a new post and send this to the database"""

            newpost = PostAddGet(Post_ID= uuid4(),
                            User_Email = useremail,
                            Post_Text = newpostinf.Post_Text, 
                            Creation_DateTime = datetime.now(timezone.utc))
            
            statement = insert(Post).values(**newpost.model_dump())

            session.execute(statement)
            session.commit()
            _update_cached_posts(useremail, None)
            return newpost
        
        except Exception as e:
            handle_server_error(f"{current_func} error: {e}")
        


@router_posts.post("/DeletePost", response_model=Message, responses = {200: {"model": Message}})
def delete_post(token: TokenDep, newpost: PostDelete, 
                      session: SessionDep):
    """
    Delete a post. If it does not exist then still the enpoint returns Success.
    """
    current_func = currentframe().f_code.co_name
    useremail = verify_token(token, session)
    if useremail:
        try:
            statement = delete(Post).where(Post.User_Email == useremail).where(Post.Post_ID == newpost.Post_ID)
            session.execute(statement)
            session.commit()
            return JSONResponse(status_code=200, content={"detail": 'Success'})
        except Exception as e:
            handle_server_error(f"{current_func} error: {e}")


_cache = TTLCache(ttl=300, maxsize=1024)
"""we use TTLCache because consecutive requests for the same user's posts should return cached data for
up to 5 minutes"""

def _get_cached_posts(useremail):
   return _cache.get(useremail)

def _update_cached_posts(useremail, posts, clear = True):
    if posts and not clear:
        _cache[useremail] = posts
    if clear:
        _cache.pop(useremail, None)


def _get_posts(useremail, session):
    """separate function for getting posts from the database"""
    current_func = currentframe().f_code.co_name
    try:
        query = select(Post).where(Post.User_Email == useremail)
        result = session.execute(query)
        return result.scalars().all()
    except Exception as e:
        handle_server_error(f"{current_func} error: {e}")


async def Validate_Post_Text(request, call_next):
    """The function implements request validation to limit the size. 
    The payload should not exceed 1 MB in size, and if it does, return an appropriate error response."""
    
    if request.url.path == "/posts/AddPost":
        request_json = await request.json()
        PostText = request_json.get("Post_Text")
        if len(PostText.encode('utf-8')) > 1048576:
            return JSONResponse(status_code=413, content={"detail": "Post_Text size exceeds 1 MB"})
    response = await call_next(request)
    return response



        

