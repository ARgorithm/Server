from fastapi import APIRouter,status,Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from datetime import timedelta

from ..core.auth import get_current_user,create_access_token,Token
from ..core.database import users_db
from ..model.utils import Account,NotFoundError,AlreadyExistsError
from ..main import config

users_api = APIRouter()

@users_api.post("/users/verify")
async def user_token_verify(user:str=Depends(get_current_user)):
    return JSONResponse()

@users_api.post("/users/register")
async def user_register(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        if config().AUTH != "ENABLED":
            raise AttributeError("Auth disabled")
        new_acc = Account(
            email=form_data.username,
            password=form_data.password
        )
        await users_db.register_user(new_acc)
        return JSONResponse(content={"status":"successful"})
    except AttributeError as ae:
        raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="AUTH diabled"        
    ) from ae
    except AlreadyExistsError as aee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email is already registered"
        ) from aee
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="account registration failed"
        ) from ex

@users_api.post("/users/login",response_model=Token)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        if config().AUTH != "ENABLED":
            raise AttributeError("Auth disabled")
        acc = await users_db.search_email(form_data.username)
        assert not acc.black_list, HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="blacklisted credentials"
        )
        access = acc.log_in(form_data.password)
        if access:
            token = create_access_token(data={"sub" : acc.email},expires_delta=timedelta(days=15))
            return {"access_token": token, "token_type": "bearer"}
        raise ValueError("Incorrect Password")
    except NotFoundError as nfe:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="email not found"        
    ) from nfe
    except AttributeError as ae:
        raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="AUTH diabled"        
    ) from ae
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="login failed"
        ) from ex