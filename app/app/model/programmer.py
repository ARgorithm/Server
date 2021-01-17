"""Handles the programmer model and utility classes
"""
import uuid
from datetime import datetime
from pydantic import BaseModel

from ..main import logger
from .utils import get_password_hash,Account,NotFoundError,AlreadyExistsError

class Programmer(Account):
    """Programmer model
    """
    public_id:str
    admin:bool
    confirmed:bool
    join_time:datetime
    black_list:bool

    def describe(self,hide_password=True):
        """returns programmer data"""
        res = self.__dict__()
        if hide_password:
            del res['password']
        return res

class ProgrammerManager():
    """Programmer manager class handles the programmers in the database
    """
    def __init__(self,source):
        self.register = source

    async def search_email(self,email:str):
        """searches programmer by email
        """
        data = await self.register.search('email',email)
        if data:
            return Programmer(**data[0])
        raise NotFoundError('programmer not found')

    async def search_public_id(self,public_id:str):
        """searches programmer by public_id
        """
        data = await self.register.search('public_id',public_id)
        if data:
            return Programmer(**data[0])
        raise NotFoundError('programmer not found')
    
    async def register_programmer(self,data:Account,admin=False):
        """registers new programmer"""
        try:
            existing = await self.search_email(data.email)
            raise AlreadyExistsError("email already registered") 
        except NotFoundError as nfe:
            new_account = Programmer(
                email=data.email,
                password=get_password_hash(data.password),
                public_id=str(uuid.uuid4()),
                admin=admin,
                join_time=datetime.now(),
                confirmed=False,
                black_list=False
            )
            await self.register.insert(new_account)
            logger.info(f"new programmer - {new_account.email}")
            return True
        except Exception as ex:
            logger.exception(ex)
            raise ex

    async def delete_programmer(self,email:str):
        """deletes existing programmer"""
        existing = await self.search_email(email)
        await self.register.delete(email)
        logger.info(f"deleted programmer - {existing.email}")
        return True

    async def black_list(self,email:str):
        """blacklist programmer"""
        programmer = await self.search_email(email)
        programmer.black_list = True
        programmer.admin = False
        await self.register.update(email,programmer)
        logger.info(f"blacklisted programmer - {programmer.email}")
        return True

    async def white_list(self,email:str):
        """whitelist programmer"""
        programmer = await self.search_email(email)
        programmer.black_list = False
        await self.register.update(email,programmer)
        logger.info(f"whitelisted programmer - {programmer.email}")
        return True
    
    async def grant(self,email:str):
        """grants administrator priveleges to programmer"""
        programmer = await self.search_email(email)
        if programmer.black_list:
            raise AttributeError("account is blacklisted")
        programmer.admin = True
        await self.register.update(email,programmer)
        logger.info(f"granted admin access - {programmer.email}")
        return True

    async def revoke(self,email:str):
        """revokes administrator priveleges from programmer"""
        programmer = await self.search_email(email)
        programmer.admin = False
        await self.register.update(email,programmer)
        logger.info(f"revoked admin access - {programmer.email}")
        return True
