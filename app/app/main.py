"""The main file that has to run by uvicorn
"""
import os
import uvicorn
import uuid
import logging
import time
from uvicorn.logging import ColourizedFormatter
from fastapi import FastAPI,Request
from fastapi import UploadFile,File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseSettings,BaseModel

STORAGE_FOLDER = "./app/uploads"
if not os.path.exists(os.path.join(os.getcwd(),STORAGE_FOLDER)):
    os.mkdir(STORAGE_FOLDER)
if not os.path.isfile(os.path.join(os.getcwd(),STORAGE_FOLDER,'__init__.py')):
    with open(os.path.join(STORAGE_FOLDER,'__init__.py'),'w+') as init:
        init.write("")

class Settings(BaseSettings):
    """Read env variables from environment
    """
    SECRET_KEY:str = "secret"
    AUTH:str="DISABLED"
    MAIL:str="DISABLED"
    DATABASE:str="DISABLED"
    DB_ENDPOINT:str="localhost"
    DB_PORT:int=27017
    DB_USERNAME:str=""
    DB_PASSWORD:str=""
    ADMIN_EMAIL:str="sample@email.com"
    ADMIN_PASSWORD:str="test123"

    class Config:
        case_sensitive=True

app = FastAPI()
config = Settings()
templates = Jinja2Templates(directory="app/templates")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

standard = logging.StreamHandler()
standard.setLevel(logging.INFO)

detailed =  logging.FileHandler(os.path.join(STORAGE_FOLDER,'server.log'),'a')
detailed.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)s] : %(message)s')
detailedformatter = ColourizedFormatter('%(asctime)s - [%(levelname)s] : %(name)s - %(message)s')
standard.setFormatter(formatter)
detailed.setFormatter(detailedformatter)
logger.addHandler(detailed)
logger.addHandler(standard)

from .core import api_setup

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = uuid.uuid4()
    logger.debug(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.debug(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
    
    return response

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