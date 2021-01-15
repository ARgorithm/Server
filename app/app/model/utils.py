import os
import re
import unicodedata
from passlib.context import CryptContext
from pydantic import BaseModel

from ..main import config

class Account(BaseModel):
    """Model for both types of accounts
    """
    email:str
    password:str

    def log_in(self,attempted_password):
        """checks password and returns boolean
        """
        return verify_password(attempted_password,self.password)

class NotFoundError(Exception):
    """Exception class to handle situations where entity does not exist in database
    """
    pass

class AlreadyExistsError(Exception):
    """Exception class to handle situations where entity already exists in database
    """
    pass

ALLOWED_EXTENSIONS = {'py'}
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
_windows_device_files = (
    "CON",
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "LPT1",
    "LPT2",
    "LPT3",
    "PRN",
    "NUL",
)

def allowed_file(filename):
    """checks whether filename is valid or not
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename: str) -> str:
    """checks whether filename is secure or not"""
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )

    if (
        os.name == "nt"
        and filename
        and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = f"_{filename}"

    return filename

def verify_password(plain_password, hashed_password):
    """verifies password hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """generates password has
    """
    return pwd_context.hash(password)