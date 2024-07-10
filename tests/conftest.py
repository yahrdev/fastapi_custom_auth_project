"""the file for tests configuration. To run tests: pytest -v  tests/"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import json
from constants import  testing_file
from fastapi.testclient import TestClient
from posts.models import BasePost 
from auth.models import BaseUser
from config import settings
from main import app

#test database and session creation

engine_test = create_engine(settings.DB_URL)
session_maker = sessionmaker(expire_on_commit=False, bind=engine_test)


@pytest.fixture(autouse=True)
def prepare_database():
    """the database will be cleared after each test"""
    assert settings.MODE == "TEST"
    BaseUser.metadata.create_all(engine_test)
    BasePost.metadata.create_all(engine_test)
    yield
    BasePost.metadata.drop_all(engine_test)
    BaseUser.metadata.drop_all(engine_test)
        




@pytest.fixture()
def ac():
    """Pytest fixture to provide an Client for testing the ASGI app."""
    return TestClient(app)



def GetJson() -> list:
    """loading data to use in tests"""
    try:
        f = open(r"tests/auth_testcases.json", 'r')
        UsersDB = json.load(f)
        return UsersDB
    except:
        print('Test JSON can not be loaded')


def readtext() -> str:
    """the function to load big data files"""
    try:
        f = open(testing_file, 'r')
        text = f.read()
        return text
    except:
        print("QA error")
    


def register(ac: TestClient, email, password):
    """to register a test user. Will be used in each test"""
    response = ac.post('/auth/Signup', json = {
                "username": email,
                "password": password,
                })

    return response



def login(ac: TestClient, email, password):
    """to login a test user. Will be used in each test"""
    response = ac.post('/auth/Login', data = {
                "username": email,
                "password": password,
                })
    return response

