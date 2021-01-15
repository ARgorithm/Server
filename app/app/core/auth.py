"""Authentication and authorization tools
"""
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from typing import Optional
from datetime import datetime,timedelta
from jose import JWTError, jwt
from pydantic import BaseModel 

from ..main import config
from .database import users_db,programmers_db
from ..model.utils import NotFoundError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login',auto_error=config.AUTH=="ENABLED")

class Token(BaseModel):
    """Authorization token response
    """
    access_token: str
    token_type: Optional[str]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generates a access token busing the email

    Args:
        data (dict): data to be encoded with jwt
        expires_delta (Optional[timedelta], optional): expiration time.

    Returns:
        token: jwt token generated
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Check authorization and get account email
    """
    if config.AUTH == "DISABLED":
        return config.ADMIN_EMAIL
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        try:
            user = await users_db.search_email(email)
        except NotFoundError as nfe:
            raise credentials_exception
        if user.black_list:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Blacklisted credentials"
            )
        return email
    except JWTError:
        raise credentials_exception
    

async def get_current_programmer(token: str = Depends(oauth2_scheme)):
    """Check authorization and get account email
    """
    if config.AUTH == "DISABLED":
        return config.ADMIN_EMAIL
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        try:
            programmer = await programmers_db.search_email(email)
        except NotFoundError as nfe:
            raise credentials_exception
        if programmer.black_list:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Blacklisted credentials"
            )
        return email
    except JWTError:
        raise credentials_exception
    return email

async def get_admin_programmer(token: str = Depends(oauth2_scheme)):
    """Check authorization and get account email
    """
    if config.AUTH == "DISABLED":
        return config.ADMIN_EMAIL
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        try:
            programmer = await programmers_db.search_email(email)
        except NotFoundError as nfe:
            raise credentials_exception
        if not programmer.admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin priveleges needed"
            )
        return email
    except JWTError:
        raise credentials_exception
    return email
