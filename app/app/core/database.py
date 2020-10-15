import pymongo

client = pymongo.MongoClient("mongodb+srv://AlanJohn:ClawIsAmaze@cluster0.7tf44.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.argorithm
user_collection = db.users

users = [
    {
        "name" : "Alan John" , 
        "email" : "alansandra2013@gmail.com"
    }
]
