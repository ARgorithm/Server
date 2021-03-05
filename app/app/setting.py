import os
import sys
import socket
from pydantic import BaseSettings

STORAGE_FOLDER = "/tmp/argorithm"
if not os.path.exists(os.path.join(os.getcwd(),STORAGE_FOLDER)):
    os.mkdir(STORAGE_FOLDER)
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

    class Config:
        case_sensitive=True

config = Settings()