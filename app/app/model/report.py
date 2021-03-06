import uuid
from typing import Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel

from .sql_utils import ReportType

class BugReport(BaseModel):
    """Bugs reported by user or system in a particular argorithms"""
    report_id:str = ""
    argorithmID:str = ""
    bug_type:ReportType
    timestamp:datetime = datetime.now()
    description:dict = {}
    checked:bool = False

class UserDetail(BaseModel):
    text:str = ""
    severe:bool = False
    test_params:Optional[dict] = None

class SystemDetail(BaseModel):
    text:str = ""

class MetricsAlert(BaseModel):
    """Reports generated from prometheus alerts"""
    pass

class ReportManager():
    """Handles all reports"""
    
    def __init__(self,source):
        self.register = source

    async def add_user_report(self,argorithm_id,bugdata,user):
        br = BugReport(
            report_id=str(uuid.uuid4()),
            argorithmID=argorithm_id,
            bug_type=ReportType.User,
            timestamp=datetime.now(),
            description=bugdata.dict(),
            checked=False
        )
        await self.register.insert(br)

    async def add_system_report(self,argorithm_id,bugdata):
        pass

    async def add_alert_report(self,bugdata):
        pass

    async def compile_data(self,argorithm_id:str):
        """Report generation
        """
        pass