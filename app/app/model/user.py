import os
from werkzeug.security import generate_password_hash, check_password_hash
# import jwt

class User:
    def __init__(self,email,password,admin=False):
        self.email = email
        self.password = password
        self.admin = admin
        self.confirmed = False
        self.black_list = False

    def describe(self,security=True):
        res = {
            "email" : self.email,
            "password" : self.password,
            "admin" : self.admin,
            "confirmed" : self.confirmed,
            "black_list" : self.black_list
        }
        if security:
            del res['password']
        return res

    def verify_password(self,attempt):
        print(self.password)
        print(attempt)
        curr = check_password_hash(self.password,attempt)
        print(curr)
        return curr

class UserManager:

    def __init__(self,register):
        self.register = register
    
    def search_user(self,email):
        try:
            data = self.register.search(name=email,key="email")
            return User(
                email=data['email'],
                password=data['password'],
                admin=data['admin']
            )
        except:
            return None

    def register_user(self,data,admin=False):
        try:
            if self.search_user(data['email']) == None:
                user = User(
                    email=data['email'],
                    password=generate_password_hash(data['password']),
                    admin=admin
                )
                self.register.insert(key='admin',value=user.describe(security=False))
                return {"status":"success"}
            else:
                return {"status":"already exists"}
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }

    def login(self,data):
        try:
            user = self.search_user(data['email'])
            if user == None:
                return {
                    "status" : "Not Found"
                }
            if user.verify_password(data['password']):
                return {
                    "status" : "successful"
                }
            return {
                "status" : "failure"
            }
            
            
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }


## When adding mail support
class UserManagerWithMail:
    pass 

    
        
    
