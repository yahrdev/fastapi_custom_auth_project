"""The model of the Post table"""

from sqlalchemy import  String, TIMESTAMP, ForeignKey, Column, Text, Uuid
from datetime import datetime, timezone
from auth.models import User
from sqlalchemy.orm import declarative_base, Mapped,  mapped_column

BasePost = declarative_base()

class Post(BasePost):
    __tablename__ = 'post'

    
    """we do not use autoincrement because database should not generate Uuid automatically when
        inserting a new entry"""
    Post_ID: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, autoincrement=False)

    Post_Text: Mapped[Text] = mapped_column(Text(1000000), nullable=False)
    User_Email: Mapped[String] = mapped_column(String(320), ForeignKey(User.email), nullable=False)

    #Creation_DateTime is generated automatically
    Creation_DateTime: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.now(timezone.utc), nullable=False)



