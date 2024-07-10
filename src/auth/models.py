"""The User model"""

from sqlalchemy import Integer, String, Text

from sqlalchemy.orm import  Mapped,  mapped_column

from sqlalchemy.orm import declarative_base

BaseUser = declarative_base()


class User(BaseUser):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[Text] = mapped_column(String(320), index=True, nullable=False)
    hashed_password: Mapped[Text] = mapped_column(String(1024), nullable=False)


    
    


