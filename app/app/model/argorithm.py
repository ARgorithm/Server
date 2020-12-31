import os
import json
import importlib
import ARgorithmToolkit
from werkzeug.utils import secure_filename
from ..main import app

UPLOAD_FOLDER = '/app/app/uploads'
ALLOWED_EXTENSIONS = {'py'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Argorithm:

    def __init__(self,**kwargs):
        self.maintainer = kwargs['maintainer']
        self.argorithmID = kwargs['argorithmID']
        self.file = kwargs['filename']
        self.function = kwargs['function']
        self.parameters = kwargs['parameters']
        self.description = kwargs['description']
        self.default = kwargs['default']

    def describe(self):
        return {
            "maintainer": self.maintainer,
            "argorithmID" : self.argorithmID,
            "parameters" : self.parameters,
            "filename" : self.file,
            "function" : self.function,
            "description" : self.description,
            "default" : self.default
        }

    def __str__(self):
        return self.argorithmID

    def run_code(self,parameters):
        filepath = "app.uploads." + self.file[:-3]
        module = importlib.import_module(filepath)
        func = getattr(module , self.function)
        parameters = self.default if parameters==None else parameters
        output = func(**parameters)
        res = [x.content for x in output.states]
        return res

class ArgorithmManager():

    def __init__(self , source):
        self.register = source

    def list(self):
        return self.register.list(keys=["argorithmID","parameters","description","maintainer"])

    def search(self,argorithmID):
        # print(argorithmID)
        try:
            return Argorithm(**self.register.search(name=argorithmID,key="argorithmID"))
        except:
            return None

    def insert(self,data,file):
        if self.search(data['argorithmID']) != None:
            return {"status" : "argorithmID already exists"}
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if filename != data['file']:
                return {
                    "status" : "filename was invalid"
                } 
            count = 1
            final_filename = filename
            while os.path.isfile(os.path.join(UPLOAD_FOLDER, final_filename)):
                final_filename = filename[:-3]+f"_{count}"+filename[-3:]
                count+=1
            file.save(os.path.join(UPLOAD_FOLDER, final_filename))
            metadata = Argorithm(
                maintainer=data['maintainer'],
                argorithmID=data['argorithmID'],
                filename=final_filename,
                function=data['function'],
                parameters=data['parameters'],
                description=data['description'],
                default=data["default"]
            )
            self.register.insert(key=data['argorithmID'] , value= metadata.describe())
            return {
                "status" : "successful"
            }
        return {"status" : "not python file"}

    def update(self,data,file):
        function = self.search(data['argorithmID'])
        if function==None:
            return {"status" : "not present"}
        try:
            assert data['maintainer'] == function.maintainer or data['maintainer'] == app.config["ADMIN_EMAIL"] , AssertionError("Authorization failed")
            file.save(os.path.join(UPLOAD_FOLDER, function.file))
            return {"status" : "successful"}
        except Exception as e:
            return {
                "status" : "error",
                "message" : str(e)  
            }

    def process(self,data):
        function = self.search(data['argorithmID'])
        if function==None:
            return {"status" : "not present"}
        try:
            # print(data["parameters"])
            return {
                "status" : "run_parameters",
                "data" : function.run_code(data["parameters"])
                }
        except:
            try:
                return {
                    "status" : "run_default",
                    "data" : function.run_code(None)
                }
            except Exception as e:
                return {"status" : "error",
                    "message" : str(e)
                }

    def delete(self,data):
        function = self.search(data['argorithmID'])
        if function==None:
            return {"status" : "not present"}
        try:
            assert data['maintainer'] == function.maintainer or data['maintainer'] == app.config["ADMIN_EMAIL"] , AssertionError("Authorization failed")
            to_be_deleted = function.file
            # print(os.path.join(UPLOAD_FOLDER , to_be_deleted))
            os.remove(os.path.join(UPLOAD_FOLDER , to_be_deleted))
            self.register.delete(key="argorithmID",value=function.argorithmID)
            return {"status" : "successful"}
        except Exception as e:
            return {"status" : "error",
                    "message" : str(e)  
                }