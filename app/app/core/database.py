"""database utilities
"""
import os
import json
from motor import motor_asyncio
from databases import Database
from pydantic import BaseModel
from pymongo import monitoring

from ..main import config,STORAGE_FOLDER,app
from ..model.argorithm import ARgorithmManager
from ..model.programmer import ProgrammerManager
from ..model.user import UserManager
from ..model.report import ReportManager
from ..model.sql_utils import Base
from ..model.utils import Account , AlreadyExistsError
from ..monitoring import logger,DatabaseMonitor

admin_account = Account(
    email=config().ADMIN_EMAIL,
    password=config().ADMIN_PASSWORD,
)

pk = {
        "argorithm" : "argorithmID",
        "user" : "email",
        "programmer" : "email",
        "reports" : "report_id"
    }


def clean(res):
    """Cleans data recieved from SQLITE database
    """
    if res:
        item = {}
        for key,value in res.items():
            try:
                item[key] = value
            except:
                pass
        return item
    return None

class SQLSource:
    def __init__(self,label):
        self.database = Database(config().DB_ENDPOINT)
        self.table = Base.metadata.tables[label]
        self.label = label
        self.primary_key = list(self.table.primary_key.columns)[0]

    async def list(self):
        await self.database.connect()
        query = self.table.select()
        value = await self.database.fetch_all(query=query)
        await self.database.disconnect()
        if value:
            return [clean(row) for row in value]
        else:
            return None


    async def search(self,key,value):
        await self.database.connect()
        query = self.table.select().where(self.table.columns[key] == value)
        value = await self.database.fetch_all(query=query)
        await self.database.disconnect()
        if value:
            return [clean(row) for row in value]
        else:
            return None

    async def insert(self,data:BaseModel):
        await self.database.connect()
        query = self.table.insert()
        value = data.dict()
        await self.database.execute(query=query,values=value)
        await self.database.disconnect()

    async def update(self,key,value):
        await self.database.connect()
        query = self.table.update().where(self.primary_key == key)
        value = value.dict()
        await self.database.execute(query,values=value)
        await self.database.disconnect()

    async def delete(self,key):
        await self.database.connect()
        query = self.table.delete().where(self.primary_key == key)
        await self.database.execute(query)
        await self.database.disconnect()

class MongoSource:
    """database manager for mongodb database

    attributes:
        label(str): The model for which collection is managed
        collection(motor.AsyncIOMotorCollection): The collection of documents
    """
    def __init__(self,label):
        assert label in ['user','programmer','argorithm','reports']
        logger.info(f"Connecting to mongodb collection={label}...")
        if "mongodb+srv" in config().DB_ENDPOINT:
            client = motor_asyncio.AsyncIOMotorClient(config().DB_ENDPOINT)
        else:    
            client = motor_asyncio.AsyncIOMotorClient(
                config().DB_ENDPOINT,port=config().DB_PORT,
                username=config().DB_USERNAME,
                password=config().DB_PASSWORD
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

class TestSource:
    """
    Datasource for testing functionalities without database connectivity

    Attributes:
        data (dict): The data object that contains emulates database storage
        label (str) : The label for this datasource
    """
    def __init__(self,label):
        self.data = []
        self.label = label
    
    async def list(self):
        return self.data

    async def insert(self,model):
        self.data.append(model.__dict__)

    async def search(self,key,value):
        for model in self.data:
            if model[key] == value:
                return [model]
        return None

    async def delete(self,key):
        self.data = [x for x in self.data if x[pk[self.label]] != key]

    async def update(self,key,value):
        new_data = []
        for x in self.data:
            if x[pk[self.label]] == key:
                new_data.append(value)
            else:
                new_data.append(x)
        self.data = new_data

argorithm_db , users_db , programmers_db = None , None , None

if config().TESTING == "ENABLED":
    argorithm_db = ARgorithmManager(source=TestSource(label="argorithm"))
    users_db = UserManager(source=TestSource(label='user'))
    programmers_db = ProgrammerManager(source=TestSource(label="programmer"))
    reports_db = ReportManager(source=TestSource(label="reports"))
elif config().DATABASE == "DISABLED":
    argorithm_db = ARgorithmManager(source=SQLSource(label="argorithm"))
    users_db = UserManager(source=SQLSource(label='user'))
    programmers_db = ProgrammerManager(source=SQLSource(label="programmer"))
    reports_db = ReportManager(source=SQLSource(label="reports"))
else:
    monitoring.register(DatabaseMonitor())
    argorithm_db = ARgorithmManager(source=MongoSource(label="argorithm"))
    users_db = UserManager(source=MongoSource(label='user'))
    programmers_db = ProgrammerManager(source=MongoSource(label="programmer"))
    reports_db = ReportManager(source=MongoSource(label="reports"))
        
@app.on_event("startup")
async def admincreds():
    """creates admin account in database
    """
    if config().DATABASE == "MONGO":
        await argorithm_db.register.setup_indexes()
        await users_db.register.setup_indexes()
        await programmers_db.register.setup_indexes()
    try:
        await programmers_db.register_programmer(admin_account,admin=True)
        await users_db.register_user(admin_account)
    except Exception:
        pass
    logger.info("Admin accounts created")