"""Handles caching for argorithm execution
"""
import json
import aioredis

from ..main import config

def convert_to_key(req):
    key = '$' + req['argorithmID'] + "_" + str(hash(json.dumps(req['parameters'])))
    return key
    
def convert_to_value(states):
    value = json.dumps(states)
    return value

class LRUCache:
    
    def __init__(self):
        self.redis_endpoint = (config.REDIS_HOST,config.REDIS_PORT)
        self.redis_password = config.REDIS_PASSWORD
        
    async def get_data(self,req):
        hashedkey = convert_to_key(req)
        redis = await aioredis.create_redis_pool(
            self.redis_endpoint,
            password=self.redis_password if self.redis_password else None
        )
        value = await redis.get(hashedkey)
        redis.close()
        await redis.wait_closed()
        if value:
            return json.loads(value)
        return None
    
    async def set_data(self,req,states):
        hashedkey = convert_to_key(req)
        value = convert_to_value(states)
        redis = await aioredis.create_redis_pool(
            self.redis_endpoint,
            password=self.redis_password if self.redis_password else None
        )
        await redis.set(hashedkey,value)
        redis.close()
        await redis.wait_closed()
    
    async def clear(self,argorithmID):
        redis = await aioredis.create_redis_pool(
            self.redis_endpoint,
            password=self.redis_password if self.redis_password else None
        )
        cur = b'0'
        netlist = []
        while cur:
            cur, keys = await redis.scan(cur, match=f'*{argorithmID}*')
            netlist += keys
        print(netlist)
        for key in netlist:
            await redis.delete(key.decode())
        redis.close()
        await redis.wait_closed()
