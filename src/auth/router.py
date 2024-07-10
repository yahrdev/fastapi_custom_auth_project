from fastapi import APIRouter, Depends, HTTPException
from database import get_session
from typing import Annotated, Any
from auth.schemas import UserCreate, UserHashed, Message
from auth.auth_base import verify_password, create_token, create_hashed_pasword, verify_user, user_exists
from sqlalchemy import insert
from auth.models import User
from logging import error
from fastapi.responses import JSONResponse
from inspect import currentframe
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError


#current_func is the name of the current function. Just for understandable error

router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"], 
    responses={500: {"model": Message},
               401: {"model": Message}})



@router_auth.post("/Signup", responses = {201: {"model": Message},
                                          409: {"model": Message}},
                                          status_code=201)
def Signup(newuser: UserCreate, session: Annotated[Any, Depends(get_session)]):
    """
    Create a user with the following information:

    - **id**: str, is generated automatically
    - **email**: user's email
    - **hashed_password**: a password hashed using CryptContext
    """
    current_func = currentframe().f_code.co_name   
    if user_exists(newuser.username, session=session) == False:   #because it can be empty also
        try:
            """
            hash user's password and create a model in order to write to the database
            afterwards create a token
            """

            hashed_password = create_hashed_pasword(newuser.password)
            hashed_user = UserHashed(email=newuser.username,
                                    hashed_password=hashed_password)
            
            statement = insert(User).values(**hashed_user.model_dump())

            session.execute(statement)
            session.commit()
            token = create_token(newuser.username)
            return JSONResponse(status_code=201, content=token)
        except Exception as e:
            error(f"{current_func} error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    else:
        raise HTTPException(status_code=409, detail="The user already registered")
    

@router_auth.post("/Login", responses = {200: {"model": Message}})
def Login(loginuser: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Any, Depends(get_session)]):
    """
    Validate user's information. Check the following data:

    - **email**
    - **password**
    """
    current_func = currentframe().f_code.co_name  
    try:
        """
        validate user's data using pydantic model, check if a user exists, 
        check the user's password, create a token and return it
        """
        checked_data = UserCreate(username=loginuser.username, password=loginuser.password) 
        hashed_password = verify_user(checked_data.username, session)
        if not verify_password(checked_data.password, hashed_password):
            error(f"{current_func} error: Wrong password")
            raise HTTPException(status_code=401, detail="Unauthorized")
        token = create_token(checked_data.username)
        return JSONResponse(status_code=200, content=token)
    
    #the error for UserLogin model creation:
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    #catch Wrong password error: 
    except HTTPException as e:               
        raise e
    except Exception as e:
        error(f"{current_func} error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")





