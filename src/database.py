"""Creation of a database session which will be used in all endpoints"""

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from config import settings
from typing import Generator, Any


engine = create_engine(settings.DB_URL)
session_maker = sessionmaker(expire_on_commit=False, bind=engine)



def get_session()  -> Generator[Session, Any, None]:
    db = session_maker()
    try:
        yield db
    finally:
        db.close()








