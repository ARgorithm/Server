
class BlankSource():
    def __init__(self,filename='db.json'):
        self.data = {}
    
    def list(self,keys=["argorithmID","parameters","description"]):
        response = []
        for x in self.data:
            opt = {}
            for key in keys:
                opt[key] = self.data[x][key]
            response.append(opt)
        return response
    
    def search(self,name,key):
        try:
            return self.data[name]
        except:
            return None

    def insert(self,key,value):
        self.data[key] = value
        
    def delete(self,key,value):
        del self.data[value]
        