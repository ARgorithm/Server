import os
import sys
import socket
from pydantic import BaseSettings
import tempfile

STORAGE_FOLDER = os.path.join(tempfile.gettempdir(), "argorithm")
try:
    os.mkdir(STORAGE_FOLDER)
except FileExistsError:
    pass
sys.path.append(STORAGE_FOLDER)

class Settings(BaseSettings):
    """Read env variables from environment
    """
    SECRET_KEY:str = "secret"
    AUTH:str="DISABLED"
    MAIL:str="DISABLED"
    SENDGRID_API_KEY:str=""
    ENDPOINT=socket.gethostname()
    DATABASE:str="DISABLED"
    DB_ENDPOINT:str=f"sqlite:///{STORAGE_FOLDER}/sqlite.db"
    DB_PORT:int=27017
    DB_USERNAME:str=""
    DB_PASSWORD:str=""
    ADMIN_EMAIL:str="sample@email.com"
    ADMIN_PASSWORD:str="test123"
    CACHING:str="DISABLED"
    REDIS_HOST:str="127.0.0.1"
    REDIS_PORT:int=6379
    REDIS_PASSWORD:str=""
    METRICS_TOKEN:str=""
    TESTING:str="DISABLED"

    class Config:
        case_sensitive=True

def config():
    return Settings()