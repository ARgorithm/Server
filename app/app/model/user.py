"""Model for User and utility classes
"""
import uuid
from pydantic import BaseModel

from ..monitoring import logger
from .utils import get_password_hash,Account,NotFoundError,AlreadyExistsError

class User(Account):
    """User Model
    """
    public_id:str
    black_list:bool
    
    def describe(self,hide_password=True):
        """returns representation of User class"""
        res = self.__dict__
        if hide_password:
            del res['password']
        return res

class UserManager():
    """Acts as manager for all the users in database
    """

    def __init__(self,source):
        self.register = source

    async def search_email(self,email:str):
        """searches user by email
        """
        data = await self.register.search('email',email)
        if data:
            return User(**data[0])
        raise NotFoundError("user not found")

    async def search_public_id(self,public_id:str):
        """searches user by public_id
        """
        data = await self.register.search('public_id',public_id)
        if data:
            return User(**data[0])
        raise NotFoundError("user not found")
    
    async def register_user(self,data:Account):
        """registers new user account
        """
        try:
            existing = await self.search_email(data.email)
            raise AlreadyExistsError("email already registered") 
        except NotFoundError as nfe:
            pass
        new_account = User(
            email=data.email,
            password=get_password_hash(data.password),
            public_id=str(uuid.uuid4()),
            black_list=False
        )
        await self.register.insert(new_account)
        logger.info(f"new user - {new_account.email}")
        return True

    async def delete_user(self,email:str):
        """deletes existing user
        """
        existing = await self.search_email(email)
        await self.register.delete(email)
        logger.info(f"deleted user - {existing.email}")
        return True

    async def black_list(self,email:str):
        """blacklists user
        """
        user = await self.search_email(email)
        user.black_list = True
        await self.register.update(email,user)
        logger.info(f"blacklisted user - {user.email}")
        return True

    async def white_list(self,email:str):
        """whitelists user
        """
        user = await self.search_email(email)
        user.black_list = False
        await self.register.update(email,user)
        logger.info(f"whitelisted user - {user.email}")
        return True

    