from ..model.argorithm import ArgorithmManager
import os
import json
# import pymongo

# client = pymongo.MongoClient("mongodb+srv://AlanJohn:<password>@cluster0.7tf44.mongodb.net/<dbname>?retryWrites=true&w=majority")
# db = client.argorithm
# user_collection = db.users

users = [
    {
        "name" : "Alan John" , 
        "email" : "alansandra2013@gmail.com"
    }
]

class FileSource:
    def __init__(self):
        self.filename = '/app/db.json'
        if not os.path.isfile(self.filename):
            with open(self.filename,'w') as store:
                json.dump({},store)
    
    def list(self):
        with open(self.filename,'r') as store:
            register = json.load(store)
        response = [register[x] for x in register]
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

algorithms = ArgorithmManager(source=FileSource())