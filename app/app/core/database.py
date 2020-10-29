from ..model.argorithm import ArgorithmManager
from ..model.user import UserManager
import os
import json
from pymongo import MongoClient
from ..main import app

users = None
user_list = [
    {
        "email" : app.config["ADMIN_EMAIL"],
        "password" : app.config["ADMIN_PASSWORD"] ,
    }
]

class MongoSource:
    def __init__(self,collection):
        clientname = "mongodb"
        port = 27017
        username = app.config["DB_USERNAME"]
        password = app.config['DB_PASSWORD']
        self.client = MongoClient(clientname, port , username=username,password=password , connect=False)
        # print("CONNECTED")
        db = self.client.argorithms
        self.coll = db[collection]

    def list(self,keys):
        response = []
        for doc in self.coll.find():
            opt = {}
            for key in keys:
                opt[key] = doc[key]
            response.append(opt)
        return response
    
    def search(self,name,key):
        response = []
        for doc in self.coll.find({ key : name }):
            response.append(doc)
        if len(response) == 0:
            return None
        else:
            return response[0]

    def insert(self,key,value):
        self.coll.insert_one(value)

    def delete(self,key,value):
        self.coll.delete_one({key : value})
        
class FileSource:
    def __init__(self,filename='db.json'):
        self.filename = os.path.join('/app/app/uploads' , filename)
        if not os.path.isfile(self.filename):
            with open(self.filename,'w') as store:
                json.dump({},store)
    
    def list(self,keys=["argorithmID","parameters","description"]):
        response = []
        with open(self.filename,'r') as store:
            register = json.load(store)
        for x in register:
            opt = {}
            for key in keys:
                opt[key] = register[x][key]
            response.append(opt)
        return response
    
    def search(self,name,key):
        with open(self.filename , 'r') as store:
            register = json.load(store)
            # print(register)
        try:
            return register[name]
        except:
            return None

    def insert(self,key,value):
        with open(self.filename , 'r') as store:
            register = json.load(store)
        register[key] = value
        with open(self.filename,'w') as store:
            json.dump(register,store)

    def delete(self,key,value):
        # print(key)
        with open(self.filename , 'r') as store:
            register = json.load(store)
        # print(register[value])
        del register[value]
        with open(self.filename,'w') as store:
            json.dump(register,store)


DATABASE = app.config["DATABASE"]
AUTH = app.config["AUTH"]
MAIL = app.config["MAIL"]

if DATABASE == "MONGO":
    algorithms = ArgorithmManager(source=MongoSource(collection='argorithms'))
    
    if AUTH == "ENABLED":
        users = UserManager(register=MongoSource(collection='users'))
        for user in user_list:
            users.register_user(
                data=user,
                admin=True
            )    
        if MAIL == 'ENABLED':
            raise AssertionError("Mail support has not been added")

else:
    algorithms = ArgorithmManager(source=FileSource())