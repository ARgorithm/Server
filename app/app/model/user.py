import os
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid


class User:
    
    def __init__(self,public_id,email,password,black_list=False):
        self.email = email
        self.password = password
        self.public_id = public_id
        self.black_list = black_list
    
    def describe(self,hide_password=True):
        res = {
            "email" : self.email,
            "password" : self.password,
            "public_id" : self.public_id,
            "black_list" : self.black_list
        }
        if hide_password:
            del res['password']
        return res

    def verify_password(self,attempt):
        curr = check_password_hash(self.password,attempt)
        return curr


class UserManager:
    def __init__(self,register):
        self.register = register
    
    def search_user(self,email):
        try:
            data = self.register.search(name=email,key="email")
            return User(
                public_id=data['public_id'],
                email=data['email'],
                password=data['password'],
                black_list=data['black_list']
            )
        except:
            return None

    def search_public_id(self,public_id):
        try:
            data = self.register.search(name=public_id,key="public_id")
            return User(
                public_id=data['public_id'],
                email=data['email'],
                password=data['password'],
                black_list=data['black_list']
            )
        except:
            return None

    def register_user(self,data):
        try:
            if self.search_user(data['email']) == None:
                user = User(
                    public_id=str(uuid.uuid4()),
                    email=data['email'],
                    password=generate_password_hash(data['password']),
                )
                self.register.insert(key=data['email'],value=user.describe(hide_password=False))
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
                token = jwt.encode({ 
                    'public_id': user.public_id, 
                    'exp' : datetime.utcnow() + timedelta(days=30) 
                }, os.getenv("SECRET_KEY")) 
                return {
                    "status" : "successful",
                    "token" : token
                }
            return {
                "status" : "failure"
            }
            
            
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }

    def delete(self,data):
        try:
            user = self.search_user(data['email'])
            if user == None:
                return {
                    "status" : "Not Found"
                }
            self.register.delete(key="email",value=user.email)
            return {"status" : "successful"}
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }

    def black_list(self,data):
        try:
            user = self.search_user(data['email'])
            if user == None:
                return {
                    "status" : "Not Found"
                }
            user.black_list = True
            self.register.update({"email" : user.email},{"black_list" : user.black_list})
            return {"status":"successful"}
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }

    def white_list(self,data):
        try:
            user = self.search_user(data['email'])
            if user == None:
                return {
                    "status" : "Not Found"
                }
            user.black_list = False
            self.register.update({"email" : user.email},{"black_list" : user.black_list})
            return {"status":"successful"}
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }
