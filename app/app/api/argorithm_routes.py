import json
from typing import List
from fastapi import APIRouter,Depends,status
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from ..main import config,logger
from ..model.argorithm import ARgorithm
from ..model.utils import AlreadyExistsError,NotFoundError
from ..core.database import argorithm_db
from ..core.auth import get_current_programmer,get_current_user

argorithms_api = APIRouter()

@argorithms_api.get("/argorithms/list")
async def argorithms_list():
    try:
        data = await argorithm_db.list()
        return JSONResponse(content=data)
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to access argorithms"
        ) from ex

@argorithms_api.get("/argorithms/view/{argorithmid}")
async def argorithms_view(argorithmid:str):
    try:
        data = await argorithm_db.search(argorithmid)
        return JSONResponse(data.__dict__)
    except NotFoundError as nfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no such argorithm"
        )

@argorithms_api.post("/argorithms/insert")
async def argotihms_insert(file: UploadFile = File(...),data:UploadFile = File(...),maintainer:str=Depends(get_current_programmer)):
    try:
        data = json.loads((data.file.read()))
        data['maintainer'] = maintainer
        flag = await argorithm_db.insert(data,file)
        return JSONResponse()
    except AlreadyExistsError as aee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="argorithm already exists"
        ) from aee
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The file name was invalid"    
        ) from ve
    except AssertionError as ae:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="should be a .py file"
        ) from ae
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="contact administrator"
        ) from ex

class ExecutionRequest(BaseModel):
    argorithmID:str=""
    parameters:dict={}
    user:str=""

@argorithms_api.post("/argorithms/run")
async def argorithms_run(exec:ExecutionRequest,user:str=Depends(get_current_user)):
    try:
        output = await argorithm_db.process(exec)
        return JSONResponse(output)
    except NotFoundError as nfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="argorithm not found"
        ) from nfe
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="contact administrator"
        ) from ex 


@argorithms_api.post("/argorithms/update")
async def argotihms_update(file: UploadFile = File(...),data:UploadFile = File(...),maintainer:str=Depends(get_current_programmer)):
    try:
        data = json.loads((data.file.read()))
        data['maintainer'] = maintainer
        flag = await argorithm_db.update(data,file)
        return JSONResponse()
    except NotFoundError as nfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="argorithm not found"
        ) from nfe
    except AssertionError as ae:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only argorithm maintaner or admin can perform this action"
        )
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="contact administrator"
        )    

class DeletionRequest(BaseModel):
    argorithmID:str=""
    maintainer:str=config.ADMIN_EMAIL

@argorithms_api.post("/argorithms/delete")
async def argorithms_delete(d:DeletionRequest,maintainer:str=Depends(get_current_programmer)):
    try:
        d = d.__dict__
        d['maintainer'] = maintainer
        flag = await argorithm_db.delete(d)
        return JSONResponse()
    except NotFoundError as nfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="argorithm not found"
        ) from nfe
    except AssertionError as ae:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only argorithm maintaner or admin can perform this action"
        )
    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="contact administrator"
        )