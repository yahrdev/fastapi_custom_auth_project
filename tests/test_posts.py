from datetime import datetime, timezone
from uuid import uuid4
import pytest

from fastapi.testclient import TestClient
from constants import testing_email, testing_cash,  testing_password, testing_add
from sqlalchemy import insert
from conftest import session_maker,  register, readtext, login
from posts.models import Post
from posts.schemas import PostAddGet



class TestPosts:

    @pytest.fixture
    def registerlogin(self, ac):
        """we should register before testing the posts functionality"""
        response = register(ac, testing_email, testing_password)
        return response.json()["access_token"]


    def _addpost(self, ac: TestClient, registerlogin, text):
        """general function for adding posts. will be used further""" 
        response = ac.post('/posts/AddPost', json = {"Post_Text": text,}, 
                                                   params={"token": registerlogin,})
        
        return response

    def _getposts(self, ac: TestClient, registerlogin):
        """general function for getting posts. will be used further"""
        response = ac.get('/posts/GetPosts', params = {"token": registerlogin,})
        return response


    
    @pytest.mark.parametrize('text', [testing_add, ''])
    def test_AddPost(self, ac, registerlogin, text):
        """check 2 cases in one test: non empty post and empty post"""
        response = self._addpost(ac, registerlogin, text)
        if text == '':
            assert response.status_code == 422
        else:
            assert response.status_code == 200


    def test_Payload(self, ac: TestClient, registerlogin):
        """load big text < 1MB and big text > 1MB"""
        text = readtext()
        response = self._addpost(ac, registerlogin, text)
        assert response.status_code == 200
        text = text + text
        response = self._addpost(ac, registerlogin, text)
        assert response.status_code == 413 



    def test_GetPosts(self, ac: TestClient, registerlogin):
        response = self._addpost(ac, registerlogin, testing_add)
        response = ac.get('/posts/GetPosts', params = {
                    "token": registerlogin
                    })
        assert response.status_code == 200
        assert response.json()[0]["Post_Text"] == testing_add
    

 
    def test_DeletePost(self, ac: TestClient, registerlogin):
        """test deleting of existing post and non-existing post"""
        self._addpost(ac, registerlogin, testing_add)
        response = self._getposts(ac, registerlogin)
        postid = response.json()[0]["Post_ID"]
        response = ac.post('/posts/DeletePost', json = {"Post_ID": postid,},
                                                      params={"token": registerlogin,})
        assert response.status_code == 200
        postid = str(uuid4())
        response = ac.post('/posts/DeletePost', json = {"Post_ID": postid,},
                                                      params={"token": registerlogin,})
        assert response.status_code == 200



    def test_Cash(self, ac: TestClient, registerlogin):
        """test cash by comparing GetPosts endpoint results: data added through AddPost endpoint 
        with data added through the database"""

        self._addpost(ac, registerlogin, testing_add)
        self._getposts(ac, registerlogin)
        
    
        with session_maker() as session:
            post_guid = uuid4()
            newpost = PostAddGet(Post_ID= post_guid,
                            User_Email = testing_email,
                            Post_Text = testing_cash, 
                            Creation_DateTime = datetime.now(timezone.utc))
            
            statement = insert(Post).values(**newpost.model_dump())
            session.execute(statement)
            session.commit()
        
        response = self._getposts(ac, registerlogin)
        getted_response = response.json()
        assert getted_response

        found = False
        for i in getted_response:
            if (str(i["Post_ID"]) == str(post_guid)) and (i["Post_Text"] == testing_cash):
                found = True  #then cash does not work
            
        assert found == False
    
