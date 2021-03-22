"""The main file that has to run by uvicorn
"""
import os
import sys
import uvicorn
import uuid
import logging
import time
from fastapi import FastAPI,Request
from fastapi import UploadFile,File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

from .setting import config,STORAGE_FOLDER
from .core.api_setup import compile_routes
from .monitoring import MonitoringMiddleware,metrics

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(MonitoringMiddleware, filter_unhandled_paths=True)
app.add_route("/metrics", metrics)
compile_routes(app)

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