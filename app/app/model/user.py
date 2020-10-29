import os
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
from datetime import datetime,timedelta

class User:
    def __init__(self,public_id,email,password,join_time,admin=False):
        self.public_id = public_id
        self.email = email
        self.password = password
        self.admin = admin
        self.confirmed = False
        self.join_time = join_time
        self.black_list = False

    def describe(self,security=True):
        res = {
            "public_id" : self.public_id,
            "email" : self.email,
            "password" : self.password,
            "admin" : self.admin,
            "confirmed" : self.confirmed,
            "black_list" : self.black_list,
            "join_time" : self.join_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        if security:
            del res['password']
        return res

    def verify_password(self,attempt):
        # print(self.password)
        # print(attempt)
        curr = check_password_hash(self.password,attempt)
        # print(curr)
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
                admin=data['admin'],
                join_time=datetime.strptime(data['join_time'],"%m/%d/%Y, %H:%M:%S")
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
                admin=data['admin'],
                join_time=datetime.strptime(data['join_time'],"%m/%d/%Y, %H:%M:%S")
            )
        except:
            return None

    def register_user(self,data,admin=False):
        try:
            if self.search_user(data['email']) == None:
                user = User(
                    public_id=str(uuid.uuid4()),
                    email=data['email'],
                    password=generate_password_hash(data['password']),
                    admin=admin,
                    join_time=datetime.utcnow()
                )
                self.register.insert(key=data['email'],value=user.describe(security=False))
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
                    "token" : token.decode('utf-8')
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

    
        
    
