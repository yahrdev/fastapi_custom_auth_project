from passlib.context import CryptContext
from config import settings
import jwt
from datetime import datetime, timedelta, timezone
from auth.schemas import JWT_dict, Token
from logging import error
from fastapi import HTTPException
from sqlalchemy import select
from auth.models import User
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from inspect import currentframe

#current_func is the name of the current function. Just for understandable error

pass_helper = CryptContext(schemes=["bcrypt"], deprecated="auto") #for password hashing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Login")  #flow for authorization. Is used for Posts endpoints

def create_hashed_pasword(password: str) -> str:
    return pass_helper.hash(password)


def verify_password(password, hashed_password):
    return pass_helper.verify(password, hashed_password)


def create_token(username: str) -> dict:
    current_func = currentframe().f_code.co_name

    #we take 15 minutes if smth happened with our settings
    if settings.JWT_LIFETIME_MINUTES:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_LIFETIME_MINUTES)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15) 
    

    try:
        #create data for JWT token generating (a dict with sub and exp)
        payload_dict = JWT_dict(sub = username, exp = expire) 
        to_payload = payload_dict.model_dump()  
        
        token = jwt.encode(payload= to_payload, key=settings.SECRETa, algorithm=settings.ALGORITHM)
        return Token(access_token=token, token_type="bearer").model_dump()
    except Exception as e:
        error(f"{current_func} error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")





def verify_token(token: str, session: Session):
    """
    decode token, get user, check user, return user
    """
    current_func = currentframe().f_code.co_name
    try:
        decoded_dict = jwt.decode(token, key=settings.SECRETa, algorithms=settings.ALGORITHM)
        if decoded_dict:
            jwt_dict = JWT_dict(**decoded_dict)

            #to check a user in the database:
            verify_user(jwt_dict.sub, session)  
            return jwt_dict.sub
        else:
            error(f"{current_func} error: decoded_dict is empty")
            raise HTTPException(status_code=401, detail='Unauthorized')
        
    except HTTPException as e:
        raise e
    except jwt.ExpiredSignatureError as e:
        error(f"{current_func} error: {e}")
        raise HTTPException(status_code=401, detail="Unauthorized")
    except jwt.InvalidTokenError as e:
        error(f"{current_func} error: {e}")
        raise HTTPException(status_code=498, detail="Invalid Token")
    except Exception as e:
        error(f"{current_func} error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


    

def verify_user(username:str, session: Session):
    current_func = currentframe().f_code.co_name  
    user_hashed_pass = user_exists(username=username, session=session)
    if user_hashed_pass:
        return user_hashed_pass
    else:
        error(f"{current_func} error: User was not found in the database")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    


def user_exists(username: str, session: Session):
    """
    check whether a user is in the database. If the user is in the database then we return his hashed password
    """
    current_func = currentframe().f_code.co_name
    try:
        if not username:
            error(f"{current_func} error: username is empty")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        query = select(User).where(User.email == username)
        result = session.execute(query) 

        #if scalar_one() then we have error in case a user does not exist:
        result_json = result.scalar_one_or_none()  
        if result_json:
            return result_json.hashed_password 
        else:
            return False
        
    except Exception as e:
        error(f"{current_func} error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



    

