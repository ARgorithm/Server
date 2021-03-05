from fastapi import APIRouter,Depends,status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from ..main import config
from ..core.auth import get_current_user
from ..model.report import UserBugReport,SystemBugReport,MetricsAlert

report_router = APIRouter()

@report_router.post("report/user/{argorithm_id}")
def report_by_user(bug:UserBugReport,user:str=Depends(get_current_user)):
    if config.DATABASE == "DISABLED":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    pass

@report_router.post("report/system/{argorithm_id}")
def report_by_system(bug:SystemBugReport):
    if config.DATABASE == "DISABLED":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    pass

@report_router.post("report/alerts/{argorithm_id}")
def report_by_metrics():
    if config.DATABASE == "DISABLED":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    pass
