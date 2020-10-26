from ..model.argorithm import ArgorithmManager
import os
import json
from pymongo import MongoClient

users = [
    {
        "name" : "Alan John" , 
        "email" : "alansandra2013@gmail.com"
    }
]

class MongoSource:
    def __init__(self,collection='argorithms'):
        clientname = "mongodb"
        port = 27017
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
        self.client = MongoClient(clientname, port , username=username,password=password , connect=False)
        print("CONNECTED")
        db = self.client.argorithms
        self.coll = db[collection]

    def list(self):
        response = []
        for doc in self.coll.find():
            opt = {}
            keys = ["argorithmID","parameters","description"]
            for key in keys:
                opt[key] = doc[key]
            response.append(opt)
        return response
    
    def search(self,name):
        response = []
        for doc in self.coll.find({ 'argorithmID' : name }):
            response.append(doc)
        if len(response) == 0:
            return None
        else:
            return response[0]

    def insert(self,key,value):
        self.coll.insert_one(value)

    def delete(self,key):
        self.coll.delete_one({'argorithmID' : key})
        
class FileSource:
    def __init__(self,filename='db.json'):
        self.filename = os.path.join('/app/app/uploads' , filename)
        if not os.path.isfile(self.filename):
            with open(self.filename,'w') as store:
                json.dump({},store)
    
    def list(self):
        response = []
        keys = ["argorithmID","parameters","description"]
        with open(self.filename,'r') as store:
            register = json.load(store)
        for x in register:
            opt = {}
            for key in keys:
                opt[key] = register[x][key]
            response.append(opt)
        return response
    
    def search(self,name):
        with open(self.filename , 'r') as store:
            register = json.load(store)
            print(register)
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

    def delete(self,key):
        print(key)
        with open(self.filename , 'r') as store:
            register = json.load(store)
        print(register[key])
        del register[key]
        with open(self.filename,'w') as store:
            json.dump(register,store)


DATABASE = os.getenv('DATABASE')
print(f"DATABASE from env = {DATABASE}")
if DATABASE == "MONGO":
    algorithms = ArgorithmManager(source=MongoSource())
else:
    algorithms = ArgorithmManager(source=FileSource())