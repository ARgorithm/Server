"""The model for argorithms and utility classes to handle all things related to the code and configuration of argorithms
"""
import os
import shutil
import importlib
import time
import logging
from typing import Optional
from pydantic import BaseModel,EmailStr,Field
from ..main import STORAGE_FOLDER,config,logger
from .utils import secure_filename,allowed_file,NotFoundError,AlreadyExistsError

execution_logger = logging.Logger(__name__)
execution_handler =  logging.FileHandler(os.path.join(STORAGE_FOLDER,'process.log'),'a')
execution_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='[%(levelname)s] : %(asctime)s - %(message)s')
execution_handler.setFormatter(formatter)
execution_logger.addHandler(execution_handler)

class ARgorithm(BaseModel):
    """The model class for argorithms
    """
    maintainer:str=""
    argorithmID:str=""
    filename:str=""
    function:str=""
    parameters:dict={}
    description:str=""
    example:dict={}
    filedata:Optional[bytes]

    def __str__(self):
        """Return ArgorithmID
        """
        return self.argorithmID

    async def run_code(self,parameters):
        """executes argorithm code and returns StateSet
        """
        start_time = time.time()
        filepath = self.filename[:-3]
        module = importlib.import_module(filepath)
        func = getattr(module , self.function)
        parameters = self.example if parameters==None else parameters
        output = func(**parameters)
        res = [x.content for x in output.states]

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)
        execution_logger.info(f"id={self.argorithmID} - time={formatted_process_time}ms")
        return res

class ARgorithmManager():
    """The manager class that acts as an interface between the logical handling of argorithms and its physical representation
    """

    def __init__(self , source):
        self.register = source

    async def list(self):
        """list all argorithms in database
        """
        return await self.register.list()

    async def search(self,argorithmID):
        """search argorithm by ID
        """
        data = await self.register.search('argorithmID',argorithmID)
        if data:
            return ARgorithm(**data[0])
        raise NotFoundError(f"'{argorithmID}' does not exist")
    

    async def insert(self,data,file):
        """insert a argorithm to existing collectionS
        """
        try:
            func = await self.search(data['argorithmID'])
            raise AlreadyExistsError("Change argorithmID")
        except NotFoundError as ex:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                if filename != data['file']:
                    raise ValueError("invalid file name")
                count = 1
                final_filename = filename
                while os.path.isfile(os.path.join(STORAGE_FOLDER, final_filename)):
                    final_filename = filename[:-3]+f"_{count}"+filename[-3:]
                    count+=1
                if config.DATABASE == "MONGO":
                    pass 
                else:
                    with open(os.path.join(STORAGE_FOLDER, final_filename),'wb+') as buffer:
                        shutil.copyfileobj(file.file,buffer)
                try:
                    metadata = ARgorithm(
                        maintainer=data['maintainer'],
                        argorithmID=data['argorithmID'],
                        filename=final_filename,
                        function=data['function'],
                        parameters=data['parameters'],
                        description=data['description'],
                        example=data["example"]
                    )
                    if config.DATABASE == "MONGO":
                        metadata.filedata=file.file.read()
                    await self.register.insert(metadata)
                    logger.info(f"inserted new argorithm : {metadata.argorithmID} by {metadata.maintainer}")
                    return True
                except Exception as ex:
                    os.remove(os.path.join(STORAGE_FOLDER , final_filename))
                    logger.exception(ex)
                    raise ex
            raise AssertionError("File should be a python file [.py]")
        except Exception as ex:
            logger.exception(ex)
            raise ex
        

    async def update(self,data,file):
        """updates argorithm
        """
        function = await self.search(data['argorithmID'])
        try:
            assert data['maintainer'] == function.maintainer or data['maintainer'] == config.ADMIN_EMAIL , AssertionError("Authorization failed")
            function = ARgorithm(
                    maintainer=function.maintainer,
                    argorithmID=data['argorithmID'],
                    filename=function.filename,
                    function=data['function'],
                    parameters=data['parameters'],
                    description=data['description'],
                    example=data["example"]
                )
            if config.DATABASE == "MONGO":
                function.filedata = file.file.read()
            else:
                with open(os.path.join(STORAGE_FOLDER, function.filename),'wb+') as buffer:
                    shutil.copyfileobj(file.file,buffer)
            await self.register.update(function.argorithmID,function)
            logger.info(f"inserted new argorithm : {function.argorithmID} by {data['maintainer']}")
            return True
        except AttributeError as ae:
            raise ae
        except AssertionError as ae:
            raise ae
        except Exception as ex:
            logger.exception(ex)
            raise ex

    async def process(self,data):
        """executes argorithm with given parameters
        """
        data = data.__dict__
        function = await self.search(data['argorithmID'])
        if config.DATABASE == "MONGO":
            with open(os.path.join(STORAGE_FOLDER, function.filename),'wb+') as buffer:
                buffer.write(function.filedata)
        execution_logger.info(f"Process started on {function.argorithmID}")
        try:
            res = {
                "status" : "run_parameters",
                "data" : await function.run_code(data["parameters"])
                }
            if config.DATABASE == "MONGO":
                os.remove(os.path.join(STORAGE_FOLDER , function.filename))
            return res
        except:
            try:
                execution_logger.warn("Parameters could not be parsed properly")
                res = {
                    "status" : "run_example",
                    "data" : await function.run_code(None)
                }
                if config.DATABASE == "MONGO":
                    os.remove(os.path.join(STORAGE_FOLDER , function.filename))
                return res
            except Exception as ex:
                execution_logger.error(ex)
                logger.exception(ex)
                logger.critical(f"{function.argorithmID} raised an expection")
                raise ex

    async def delete(self,data):
        """deletes argorithm
        """
        function = await self.search(data['argorithmID'])
        try:
            assert data['maintainer'] == function.maintainer or data['maintainer'] == config.ADMIN_EMAIL , AssertionError("Authorization failed")
            to_be_deleted = function.filename
            await self.register.delete(function.argorithmID)
            if config.DATABASE != "MONGO":
                os.remove(os.path.join(STORAGE_FOLDER , to_be_deleted))
            logger.info(f"deleted argorithm : {function.argorithmID} by {data['maintainer']}")
            return True
        except AssertionError as er:
            raise er
        except Exception as ex:
            logger.exception(ex)
            raise ex