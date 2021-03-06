from fastapi import APIRouter,Depends,status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..main import config
from ..core.database import reports_db
from ..core.auth import get_current_user
from ..model.report import UserDetail,SystemDetail

report_router = APIRouter()

@report_router.post("report/user/{argorithm_id}")
async def report_by_user(argorithm_id:str,description:UserDetail,user:str=Depends(get_current_user)):
    try:
        await reports_db.add_user_report(argorithm_id,description,user)
        return JSONResponse()
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bug report failed"
        ) from ex


@report_router.post("report/system/{argorithm_id}")
async def report_by_system(argorithm_id:str,description:SystemDetail):
    try:
        await reports_db.add_system_report(argorithm_id,description)
        return JSONResponse()
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="bug report failed"
        ) from ex

@report_router.post("report/alerts/{argorithm_id}")
def report_by_metrics():
    pass
