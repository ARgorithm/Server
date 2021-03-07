"""The model for argorithms and utility classes to handle all things related to the code and configuration of argorithms
"""
import os
import json
import shutil
import importlib
import time
import logging
from typing import Optional
from pydantic import BaseModel,EmailStr,Field
from ARgorithmToolkit.encoders import StateEncoder
from ..setting import STORAGE_FOLDER,config
from .utils import secure_filename,allowed_file,NotFoundError,AlreadyExistsError
from ..core.cache import LRUCache
from ..monitoring import logger,PerformanceMonitor

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
        filepath = self.filename[:-3]
        module = importlib.import_module(filepath)
        func = getattr(module , self.function)
        parameters = self.example if not parameters else parameters
        output = func(**parameters)
        res = [x.content for x in output.states]
        res = json.loads(json.dumps(res,cls=StateEncoder))
        return res

class ARgorithmManager():
    """The manager class that acts as an interface between the logical handling of argorithms and its physical representation
    """

    def __init__(self , source):
        self.register = source
        self.monitor = PerformanceMonitor()

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
                    metadata.filedata=file.file.read()
                    await self.register.insert(metadata)
                    logger.info(f"inserted new argorithm : {metadata.argorithmID} by {metadata.maintainer}")
                    return True
                except Exception as ex:
                    os.remove(os.path.join(STORAGE_FOLDER , final_filename))
                    logger.exception(ex)
                    raise ex
            raise AssertionError("File should be a python file [.py]")
        except AlreadyExistsError as ae:
            raise ae
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
            function.filedata = file.file.read()
            await self.register.update(function.argorithmID,function)
            if config.CACHING == "ENABLED":
                lru = LRUCache()
                await lru.clear(function.argorithmID)
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
        lru = None
        start_time = time.perf_counter()
        self.monitor.start_execution(data)
        logger.debug(f"id={data['argorithmID']} - Exection request")
        if config.CACHING == "ENABLED":
            lru = LRUCache()
            results = await lru.get_data(data)
            if results:
                process_time = (time.perf_counter() - start_time) * 1000
                formatted_process_time = '{0:.2f}'.format(process_time)
                logger.debug(f"id={data['argorithmID']} - time={formatted_process_time}ms")
                self.monitor.end_execution(data,"CACHE",results,process_time)
                return {
                    "status" : "run_cache",
                    "data" : results
                }
        function = await self.search(data['argorithmID'])
        with open(os.path.join(STORAGE_FOLDER, function.filename),'wb+') as buffer:
            buffer.write(function.filedata)
        try:
            start_time = time.perf_counter()
            states =  await function.run_code(data["parameters"])
            process_time = (time.perf_counter() - start_time) * 1000
            formatted_process_time = '{0:.2f}'.format(process_time)
            logger.debug(f"id={data['argorithmID']} - time={formatted_process_time}ms")
            self.monitor.end_execution(data,"NORMAL",states,process_time)
            res = {
                "status" : "run_parameters",
                "data" : states
                }
            if lru:
                await lru.set_data(data,states)
            os.remove(os.path.join(STORAGE_FOLDER , function.filename))
            return res
        except:
            try:
                start_time = time.perf_counter()
                data['parameters'] = {}
                states = None
                status = "run_example"
                if lru:
                    results = await lru.get_data(data)
                    if results:
                        status = "run_cache"
                        states = results
                        process_time = (time.perf_counter() - start_time) * 1000
                    start_time = time.perf_counter()
                if states is None:
                    states = await function.run_code(None)
                    process_time = (time.perf_counter() - start_time) * 1000
                    if lru:
                        lru.set_data(data,states)
                res = {
                    "status" : status,
                    "data" : states
                }
                formatted_process_time = '{0:.2f}'.format(process_time)
                self.monitor.end_execution(
                    data,
                    "CACHE" if status == "run_cache" else "REDIRECTED",
                    states,
                    process_time 
                )
                os.remove(os.path.join(STORAGE_FOLDER , function.filename))
                logger.debug(f"id={function.argorithmID} - time={formatted_process_time}ms")
                return res
            except Exception as ex:
                self.monitor.end_execution(
                    data,
                    "ERROR",
                    [],
                    None
                )
                logger.exception(ex)
                logger.critical(f"id={data['argorithmID']} raised an expection")
                raise ex

    async def delete(self,data):
        """deletes argorithm
        """
        function = await self.search(data['argorithmID'])
        try:
            assert data['maintainer'] == function.maintainer or data['maintainer'] == config.ADMIN_EMAIL , AssertionError("Authorization failed")
            await self.register.delete(function.argorithmID)
            if config.CACHING == "ENABLED":
                lru = LRUCache()
                await lru.clear(function.argorithmID)
            logger.info(f"deleted argorithm : {function.argorithmID} by {data['maintainer']}")
            return True
        except AssertionError as er:
            raise er
        except Exception as ex:
            logger.exception(ex)
            raise ex