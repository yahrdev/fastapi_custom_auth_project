import pytest

from conftest import GetJson, register, login

from fastapi.testclient import TestClient
from src.config import settings
import jwt

@pytest.mark.parametrize("testcase", GetJson())
class TestAuth():

    """We take test cases data from the file into testcase list and use this list in the tests"""

    def _GetStatus(self, testcase, par):
        try:
            #login and register have different successful responses
            if type(testcase["status_code"]) is dict:
                checking_status = testcase["status_code"][par]
            else:
                checking_status = testcase["status_code"]
            return checking_status
        except:
            print("QA error")


    def _Check_Token(self, testcase, token):
        decoded_token = jwt.decode(token, settings.SECRETa, algorithms=[settings.ALGORITHM])
        assert "sub" in decoded_token
        assert decoded_token["sub"] == testcase["user"]
    

    def test_register(self, ac: TestClient, testcase):
        response = register(ac, email=testcase["user"], password=testcase["password"])
        assert response.status_code == self._GetStatus(testcase, "register")
        if response.status_code == 201:
            self._Check_Token(testcase, response.json()["access_token"])


    def test_double_register(self, ac: TestClient, testcase):
        """the case when a user tries to register again"""
        response = register(ac, email=testcase["user"], password=testcase["password"])
        checking_status = self._GetStatus(testcase, "login")
        if (checking_status == 201) and (response.status_code == checking_status):
            response = register(ac, email=testcase["user"], password=testcase["password"])
            assert response.status_code == 400



    def test_login(self, ac: TestClient, testcase):
        register(ac, email=testcase["user"], password=testcase["password"])
        response = login(ac, email=testcase["user"], password=testcase["password"])
        checking_status = self._GetStatus(testcase, "login")
        assert response.status_code == checking_status

        if checking_status == 200:
            self._Check_Token(testcase, response.json()["access_token"])


    def test_nonexist_login(self, ac: TestClient, testcase):
        """the case when a user did not register before login"""
        response = login(ac, email=testcase["user"], password=testcase["password"])
        checking_status = self._GetStatus(testcase, "login")
        if checking_status != 422:  #if we check the test case with non empty login and password
            assert response.status_code == 401  
        else:
            assert response.status_code == self._GetStatus(testcase, "login") 

    
