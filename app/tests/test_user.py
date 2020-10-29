from app.model.user import UserManager,User
from tests.utils import BlankSource

users = UserManager(register=BlankSource())

def test_user_register():
    status = users.register_user(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    assert status['status'] == 'success'
    status = users.register_user(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    assert status['status'] == 'already exists'

def test_search_user():
    status = users.register_user(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    user = users.search_user('sampleuser@email.com')
    assert user.email == 'sampleuser@email.com'
    user = users.search_user('sample@email.com')
    assert user == None

def test_login():
    users.register_user(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    status = users.login(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    assert status['status'] == 'successful'
    assert status['token'] != None
    status = users.login(data={
        "email" : "sampleuser@email.com",
        "password" : "testbc"
    })
    assert status['status'] == 'failure'
    status = users.login(data={
        "email" : "sampluser@email.com",
        "password" : "testabc"
    })
    assert status['status'] == 'Not Found'
    
    