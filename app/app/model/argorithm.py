"""The model for argorithms and utility classes to handle all things related to the code and configuration of argorithms
"""
import os
import shutil
import importlib
from typing import Optional
from pydantic import BaseModel,EmailStr,Field
from ..main import STORAGE_FOLDER,config
from .utils import secure_filename,allowed_file,NotFoundError,AlreadyExistsError

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

    def __str__(self):
        """Return ArgorithmID
        """
        return self.argorithmID

    async def run_code(self,parameters):
        """executes argorithm code and returns StateSet
        """
        filepath = "app.uploads." + self.filename[:-3]
        module = importlib.import_module(filepath)
        func = getattr(module , self.function)
        parameters = self.example if parameters==None else parameters
        output = func(**parameters)
        res = [x.content for x in output.states]
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
                        example=data["default"]
                    )
                    await self.register.insert(metadata)
                    return True
                except Exception as e:
                    raise e
                    os.remove(os.path.join(STORAGE_FOLDER , final_filename))
            raise AssertionError("File should be a python file [.py]")
        except Exception as ex:
            raise e
        

    async def update(self,data,file):
        """updates argorithm
        """
        function = await self.search(data['argorithmID'])
        try:
            assert data['maintainer'] == function.maintainer or data['maintainer'] == config.ADMIN_EMAIL , AssertionError("Authorization failed")
            function = ARgorithm(
                    maintainer=data['maintainer'],
                    argorithmID=data['argorithmID'],
                    filename=function.filename,
                    function=data['function'],
                    parameters=data['parameters'],
                    description=data['description'],
                    example=data["default"]
                )
            await self.register.update(function.argorithmID,function)
            with open(os.path.join(STORAGE_FOLDER, function.filename),'wb+') as buffer:
                shutil.copyfileobj(file.file,buffer)
            return True
        except AttributeError as ae:
            raise ae
        except AssertionError as ae:
            raise ae
        except Exception as ex:
            raise ex

    async def process(self,data):
        """executes argorithm with given parameters
        """
        data = data.__dict__
        function = await self.search(data['argorithmID'])
        try:
            return {
                "status" : "run_parameters",
                "data" : await function.run_code(data["parameters"])
                }
        except:
            try:
                return {
                    "status" : "run_example",
                    "data" : await function.run_code(None)
                }
            except Exception as ex:
                raise ex

    async def delete(self,data):
        """deletes argorithm
        """
        data = data.__dict__
        function = await self.search(data['argorithmID'])
        try:
            assert data['maintainer'] == function.maintainer or data['maintainer'] == config.ADMIN_EMAIL , AssertionError("Authorization failed")
            to_be_deleted = function.filename
            await self.register.delete(function.argorithmID)
            os.remove(os.path.join(STORAGE_FOLDER , to_be_deleted))
            return {"status" : "successful"}
        except AssertionError as er:
            raise er
        except FileNotFoundError as fe:
            pass
        except Exception as ex:
            raise ex