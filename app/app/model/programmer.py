import os
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
from datetime import datetime,timedelta

class Programmer:
    def __init__(self,public_id,email,password,join_time,admin=False,black_list=False):
        self.public_id = public_id
        self.email = email
        self.password = password
        self.admin = admin
        self.confirmed = False
        self.join_time = join_time
        self.black_list = black_list

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

class ProgrammerManager:

    def __init__(self,register):
        self.register = register
    
    def search_programmer(self,email):
        try:
            data = self.register.search(name=email,key="email")
            return Programmer(
                public_id=data['public_id'],
                email=data['email'],
                password=data['password'],
                admin=data['admin'],
                black_list=data['black_list'],
                join_time=datetime.strptime(data['join_time'],"%m/%d/%Y, %H:%M:%S")
            )
        except Exception as e:
            print(str(e))
            return None

    def search_public_id(self,public_id):
        try:
            data = self.register.search(name=public_id,key="public_id")
            return Programmer(
                public_id=data['public_id'],
                email=data['email'],
                password=data['password'],
                admin=data['admin'],
                black_list=data['black_list'],
                join_time=datetime.strptime(data['join_time'],"%m/%d/%Y, %H:%M:%S")
            )
        except:
            return None

    def register_programmer(self,data,admin=False):
        try:
            if self.search_programmer(data['email']) == None:
                programmer = Programmer(
                    public_id=str(uuid.uuid4()),
                    email=data['email'],
                    password=generate_password_hash(data['password']),
                    admin=admin,
                    join_time=datetime.utcnow()
                )
                self.register.insert(key=data['email'],value=programmer.describe(security=False))
                return {"status":"success"}
            else:
                return {"status":"already exists"}
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }

    def login(self,data):
        try:
            programmer = self.search_programmer(data['email'])
            if programmer == None:
                return {
                    "status" : "Not Found"
                }
            if programmer.verify_password(data['password']):
                token = jwt.encode({ 
                    'public_id': programmer.public_id, 
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
            print(str(e))
            return {"status" : "error",
                "message" : str(e)
            }

    def delete(self,data):
        try:
            programmer = self.search_programmer(data['email'])
            if programmer == None:
                return {
                    "status" : "Not Found"
                }
            self.register.delete(key="email",value=programmer.email)
            return {"status" : "successful"}
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }

    def black_list(self,data):
        try:
            programmer = self.search_programmer(data['email'])
            if programmer == None:
                return {
                    "status" : "Not Found"
                }
            programmer.admin = False
            programmer.black_list = True
            self.register.update({"email" : programmer.email},{"black_list" : programmer.black_list})
            return {"status":"successful"}
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }

    def white_list(self,data):
        try:
            programmer = self.search_programmer(data['email'])
            if programmer == None:
                return {
                    "status" : "Not Found"
                }
            programmer.black_list = False
            self.register.update({"email" : programmer.email},{"black_list" : programmer.black_list})
            return {"status":"successful"}
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }
    
    def grant(self,data):
        try:
            print(data["email"])
            programmer = self.search_programmer(data['email'])
            if programmer == None:
                return {
                    "status" : "Not Found"
                }
            if programmer.black_list:
                return {"status" : "blacklisted"}
            programmer.admin = True
            self.register.update({"email" : programmer.email},{"admin" : programmer.admin})
            return {"status":"successful"}
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }

    def revoke(self,data):
        try:
            programmer = self.search_programmer(data['email'])
            if programmer == None:
                return {
                    "status" : "Not Found"
                }
            programmer.admin = False
            self.register.update({"email" : programmer.email},{"admin" : programmer.admin})
            return {"status":"successful"}
        except Exception as e:
            return {"status" : "error",
                "message" : str(e)
            }

## When adding mail support
class ProgrammerManagerWithMail:
    pass 

    
        
    
