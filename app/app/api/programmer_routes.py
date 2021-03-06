from fastapi import APIRouter,Depends,status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import timedelta

from ..main import config
from ..core.auth import get_current_programmer,Token,create_access_token
from ..core.database import programmers_db,users_db
from ..model.utils import Account,NotFoundError,AlreadyExistsError

programmers_api = APIRouter()

@programmers_api.get("/auth")
def programmers_info():
    if config.AUTH == "DISABLED":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="authentication disabled"
        )
    return JSONResponse()

@programmers_api.post("/programmers/verify")
async def programmer_token_verify(user:str=Depends(get_current_programmer)):
    return JSONResponse()

@programmers_api.post("/programmers/register")
async def programmer_register(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        if config.AUTH != "ENABLED":
            raise AttributeError("Auth disabled")
        new_acc = Account(
            email=form_data.username,
            password=form_data.password
        )
        await programmers_db.register_programmer(new_acc)
        try:
            await users_db.register_user(new_acc)
        except AlreadyExistsError:
            pass
        return JSONResponse(
            content={"status":"successful"}
            )
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

@programmers_api.post("/programmers/login" , response_model=Token)
async def programmer_login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        if config.AUTH != "ENABLED":
            raise AttributeError("Auth disabled")
        acc = await programmers_db.search_email(form_data.username)
        assert not acc.black_list, HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="blacklisted credentials"
        )
        if config.MAIL=='ENABLED' and not acc.confirmed:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="verification required"
            )
        access = acc.log_in(form_data.password)
        if access:
            token = create_access_token(data={"sub" : acc.email},expires_delta=timedelta(days=15))
            return {"access_token": token, "token_type": "bearer"}
        raise ValueError("Incorrect Password")
    except AttributeError as ae:
        raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="AUTH diabled"        
    ) from ae
    except NotFoundError as nfe:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="email not found"        
    ) from nfe
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

@programmers_api.get("/account/verification/{public_ID}")
async def programmer_verification(public_ID):
    try:
        acc = await programmers_db.search_public_id(public_ID)
        if acc.confirmed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
            )
        await programmers_db.confirm(acc)
        return "Account verified"
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="server verification"
        ) from ex
