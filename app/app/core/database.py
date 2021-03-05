"""database utilities
"""
import os
import json
from motor import motor_asyncio,motor_tornado
from databases import Database
from pydantic import BaseModel

from ..main import config,STORAGE_FOLDER,app
from ..model.argorithm import ARgorithm,ARgorithmManager
from ..model.programmer import Programmer,ProgrammerManager
from ..model.user import User,UserManager
from ..model.utils import Account , AlreadyExistsError
from ..monitoring import logger

admin_account = Account(
    email=config.ADMIN_EMAIL,
    password=config.ADMIN_PASSWORD,
)

def clean(res):
    """Cleans data recieved from SQLITE database
    """
    if res:
        item = {}
        for key,value in res.items():
            try:
                item[key] = json.loads(value)
            except:
                item[key] = value
        return item
    return None

class FileSource:
    """manages data storage in sqlite.db
    """
    def __init__(self):
        location = os.path.join(STORAGE_FOLDER,'sqlite.db')
        self.database = Database(f"sqlite:///{location}")
        
    async def create(self):
        """Creates the tables
        """
        await self.database.connect()
        query = """CREATE TABLE argorithm(
            argorithmID varchar PRIMARY KEY,
            maintainer varchar,
            filename varchar,
            function varchar,
            description varchar,
            parameters varchar,
            example varchar,
            filedata varchar
        )"""
        await self.database.execute(query)

    async def list(self):
        """query all data from table
        """
        try:
            await self.create()
        except:
            pass
        query = "SELECT * FROM argorithm"
        rows = await self.database.fetch_all(query)
        return [clean(row) for row in rows]

    async def search(self,key,value):
        """query specific data from table
        """
        try:
            await self.create()
        except:
            pass
        query = f"SELECT * FROM argorithm where {key}='{value}'"
        rows = await self.database.fetch_all(query)
        return [clean(row) for row in rows]

    async def insert(self,data:ARgorithm):
        """insert data into table
        """
        try:
            await self.create()
        except:
            pass
        query = "INSERT INTO argorithm(_keys_) VALUES (_values_)"
        data = data.__dict__
        keys = []
        values = {}
        for key in data:
            keys.append(key)
            if isinstance(data[key],dict):
                values[key] = json.dumps(data[key])
            else:
                values[key] = data[key]
        query = query.replace('_keys_',','.join(keys))
        query = query.replace('_values_',','.join([f":{key}" for key in keys]))
        await self.database.execute_many(query,[values])

    async def update(self,key,data:ARgorithm):
        """update table data
        """
        query = f"UPDATE argorithm SET :key = :value WHERE argorithmID={key}"
        data = data.__dict__
        
    async def delete(self,key):
        """delete table data
        """
        query = f"DELETE FROM argorithm WHERE argorithmID='{key}'"
        await self.database.execute(query)

pk = {
        "argorithm" : "argorithmID",
        "user" : "email",
        "programmer" : "email"
    }

class MongoSource:
    """database manager for mongodb database

    attributes:
        label(str): The model for which collection is managed
        collection(motor.AsyncIOMotorCollection): The collection of documents
    """
    def __init__(self,label):
        assert label in ['user','programmer','argorithm']
        logger.info(f"Connecting to mongodb collection={label}...")
        if "mongodb+srv" in config.DB_ENDPOINT:
            client = motor_tornado.MotorClient(config.DB_ENDPOINT)
        else:    
            client = motor_asyncio.AsyncIOMotorClient(
                config.DB_ENDPOINT,port=config.DB_PORT,
                username=config.DB_USERNAME,
                password=config.DB_PASSWORD
            )
        database = client['argorithmdb']
        self.label = label
        self.collection = database[self.label]

    async def setup_indexes(self):
        """create indexes
        """
        self.collection.create_index(pk[self.label],unique=True)

    async def list(self):
        """query all the documents in collection
        """
        res = []
        cursor = self.collection.find()
        for document in await cursor.to_list(length=100):
            if '_id' in document:
                del document['_id']
            res.append(document)
        return res

    async def search(self,key,value):
        """search for documents in the collection
        """
        res = []
        cursor = self.collection.find({key:value})
        try:
            for document in await cursor.to_list(length=1):
                if '_id' in document:
                    del document["_id"]
                res.append(document)
        except Exception as e:
            logger.exception(e)
            raise e
        if len(res) > 0:
            return res
        return None

    async def insert(self,model:BaseModel):
        """insert documents into the collection
        """
        document = model.__dict__
        result = await self.collection.insert_one(document)
        
    async def update(self,key,value):
        """update documents in the collection
        """
        result = await self.collection.update_one({pk[self.label]:key}, {'$set': value.__dict__})

    async def delete(self,key):
        """delete documents in the collection
        """
        index = pk[self.label]
        result = await self.collection.delete_many({index:key})        

argorithm_db , users_db , programmers_db = None , None , None
if config.DATABASE == "DISABLED":
    logger.info("Connecting to sqlite...")
    argorithm_db = ARgorithmManager(source=FileSource())
else:
    argorithm_db = ARgorithmManager(source=MongoSource(label="argorithm"))
    if config.AUTH != "DISABLED":
        users_db = UserManager(source=MongoSource(label='user'))
        programmers_db = ProgrammerManager(source=MongoSource(label="programmer"))
        
@app.on_event("startup")
async def admincreds():
    """creates admin account in database
    """
    if config.DATABASE != "DISABLED":
        await argorithm_db.register.setup_indexes()
        if config.AUTH:
            try:
                await users_db.register.setup_indexes()
                await users_db.register_user(admin_account)
            except Exception as ex:
                pass
            try:
                await programmers_db.register.setup_indexes()
                await programmers_db.register_programmer(admin_account,admin=True)
            except Exception as ex:
                pass
    logger.info("Admin accounts created")