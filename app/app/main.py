"""The main file that has to run by uvicorn
"""
import os
import sys
import socket
import uvicorn
import uuid
import logging
import time
from fastapi import FastAPI,Request
from fastapi import UploadFile,File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseSettings,BaseModel

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
    DB_ENDPOINT:str="localhost"
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

app = FastAPI()
config = Settings()
templates = Jinja2Templates(directory="app/templates")

from .core import api_setup
from .monitoring import MonitoringMiddleware,metrics

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(MonitoringMiddleware, filter_unhandled_paths=True)
app.add_route("/metrics", metrics)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """The root path

    Args:
        request (Request): The request object for index.html

    Returns:
        html: return index page
    """
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("fastapi_code:app")