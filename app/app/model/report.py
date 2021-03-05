import uuid
from datetime import datetime
from pydantic import BaseModel

class UserBugReport(BaseModel):
    """Bugs reported by user in a particular argorithms"""
    report_id:str = ""
    argorithmID:str = ""
    user:str = ""
    timestamp:datetime = datetime.now()
    description:str = ""
    checked:bool = False

class SystemBugReport(BaseModel):
    """Reports generated when a particular argorithm causes an issue in mobile application"""
    report_id:str = ""
    argorithmID:str = ""
    system:str = ""
    timestamp:datetime = datetime.now()
    description:str = ""
    checked:bool = False

class MetricsAlert(BaseModel):
    """Reports generated from prometheus alerts"""
    pass

class ReportManager():
    """Handles all reports"""
    
    def __init__(self,source):
        self.register = source

    async def add_user_report(self,bug:UserBugReport):
        pass

    async def add_system_report(self,bug:SystemBugReport):
        pass

    async def add_alert_report(self,bug:MetricsAlert):
        pass

    async def compile_data(self,argorithm_id:str):
        pass