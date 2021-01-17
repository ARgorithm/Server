from fastapi import APIRouter , Depends , status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.exceptions import HTTPException

from ..core.database import programmers_db,users_db
from ..core.auth import get_admin_programmer

from ..model.utils import NotFoundError

admin_api = APIRouter()

class AdminRequest(BaseModel):
    email:str

@admin_api.post("/admin/delete_user")
async def admin_delete_user(req:AdminRequest,admin=Depends(get_admin_programmer)):
    try:
        await users_db.delete_user(req.email)
        return JSONResponse()
    except NotFoundError as nfe:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="email not found"        
        ) from nfe
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="request failed"
        ) from ex
        

@admin_api.post("/admin/delete_programmer")
async def admin_delete_programmer(req:AdminRequest,admin=Depends(get_admin_programmer)):
    try:
        await programmers_db.delete_programmer(req.email)
        return JSONResponse()
    except NotFoundError as nfe:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="email not found"        
        ) from nfe
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="request failed"
        ) from ex

@admin_api.post("/admin/black_list")
async def admin_blacklist(req:AdminRequest,admin=Depends(get_admin_programmer)):
    try:
        count = 2
        try:
            await programmers_db.black_list(req.email)
        except NotFoundError:
            count-=1
        try:
            await users_db.black_list(req.email)
        except NotFoundError:
            count-=1
        if count == 0:
            raise NotFoundError("no such email registered")
        return JSONResponse()
    except NotFoundError as nfe:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="email not found"        
        ) from nfe
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="request failed"
        ) from ex

@admin_api.post("/admin/white_list")
async def admin_whitelist(req:AdminRequest,admin=Depends(get_admin_programmer)):
    try:
        count = 2
        try:
            await programmers_db.white_list(req.email)
        except NotFoundError:
            count-=1
        try:
            await users_db.white_list(req.email)
        except NotFoundError:
            count-=1
        if count == 0:
            raise NotFoundError("no such email registered")
        return JSONResponse()
    except NotFoundError as nfe:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="email not found"        
        ) from nfe
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="request failed"
        ) from ex

@admin_api.post("/admin/grant")
async def admin_grant(req:AdminRequest,admin=Depends(get_admin_programmer)):
    try:
        await programmers_db.grant(req.email)
        return JSONResponse()
    except AttributeError as ae:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="email is blacklisted"
        )
    except NotFoundError as nfe:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="email not found"        
        ) from nfe
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="request failed"
        ) from ex

@admin_api.post("/admin/revoke")
async def admin_revoke(req:AdminRequest,admin=Depends(get_admin_programmer)):
    try:
        await programmers_db.revoke(req.email)
        return JSONResponse()
    except NotFoundError as nfe:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="email not found"        
        ) from nfe
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="request failed"
        ) from ex
