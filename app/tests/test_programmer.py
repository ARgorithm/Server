from app.model.programmer import ProgrammerManager,Programmer
from tests.utils import BlankSource

programmers = ProgrammerManager(register=BlankSource())

def test_programmer_register():
    status = programmers.register_programmer(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    assert status['status'] == 'success'
    status = programmers.register_programmer(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    assert status['status'] == 'already exists'

def test_search_programmer():
    status = programmers.register_programmer(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    programmer = programmers.search_programmer('sampleuser@email.com')
    assert programmer.email == 'sampleuser@email.com'
    programmer = programmers.search_programmer('sample@email.com')
    assert programmer == None

def test_login():
    programmers.register_programmer(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    status = programmers.login(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    assert status['status'] == 'successful'
    assert status['token'] != None
    status = programmers.login(data={
        "email" : "sampleuser@email.com",
        "password" : "testbc"
    })
    assert status['status'] == 'failure'
    status = programmers.login(data={
        "email" : "sampluser@email.com",
        "password" : "testabc"
    })
    assert status['status'] == 'Not Found'

def test_blacklisting():
    programmers.register_programmer(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    programmer = programmers.search_programmer('sampleuser@email.com')
    assert programmer.email == 'sampleuser@email.com'
    assert programmer.black_list == False
    programmers.black_list({"email" : "sampleuser@email.com"})
    programmer = programmers.search_programmer('sampleuser@email.com')
    assert programmer.email == 'sampleuser@email.com'
    assert programmer.black_list == True
    programmers.white_list({"email" : "sampleuser@email.com"})
    programmer = programmers.search_programmer('sampleuser@email.com')
    assert programmer.email == 'sampleuser@email.com'
    assert programmer.black_list == False

def test_admin():
    programmers.register_programmer(data={
        "email" : "sampleuser@email.com",
        "password" : "testabc"
    })
    programmer = programmers.search_programmer('sampleuser@email.com')
    assert programmer.email == 'sampleuser@email.com'
    assert programmer.admin == False
    programmers.grant({"email" : "sampleuser@email.com"})
    programmer = programmers.search_programmer('sampleuser@email.com')
    assert programmer.email == 'sampleuser@email.com'
    assert programmer.admin == True
    programmers.revoke({"email" : "sampleuser@email.com"})
    programmer = programmers.search_programmer('sampleuser@email.com')
    assert programmer.email == 'sampleuser@email.com'
    assert programmer.admin == False