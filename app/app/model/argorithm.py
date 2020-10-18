import os
import json
import importlib
import ARgorithmToolkit
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/app/app/uploads'
ALLOWED_EXTENSIONS = {'py'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Argorithm:

    def __init__(self,**kwargs):
        self.name = kwargs['name']
        self.file = kwargs['filename']
        self.function = kwargs['function']
        self.parameters = kwargs['parameters']
        self.description = kwargs['description']
        self.default = kwargs['default']

    def describe(self):
        return {
            "name" : self.name,
            "parameters" : self.parameters,
            "filename" : self.file,
            "function" : self.function,
            "description" : self.description,
            "default" : self.default
        }

    def __str__(self):
        return self.name

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
        return self.register.list()

    def search(self,name):
        print(name)
        try:
            return Argorithm(**self.register.search(name))
        except:
            return None

    def insert(self,data,file):
        if self.search(data['name']) != None:
            return {"status" : "name already exists"}
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
                name=data['name'],
                filename=final_filename,
                function=data['function'],
                parameters=data['parameters'],
                description=data['description'],
                default=data["default"]
            )
            self.register.insert(key=data['name'] , value= metadata.describe())
            return {
                "status" : "successful"
            }
        return {"status" : "not python file"}

    def process(self,data):
        function = self.search(data['function'])
        if function==None:
            return {"status" : "not present"}
        # try:
        try:
            print(data["parameters"])
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
            except:
                return {"status" : "error"}
            