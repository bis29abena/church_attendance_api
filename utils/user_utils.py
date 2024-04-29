from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Union, Optional
from exceptions.env_exceptions import EnvironmentNotFound

import re
import os

pwd_context = CryptContext(schemes=["bcrypt"])


class Utils:
    def __init__(self):
        pass

    def encrypt_password(self, email: str, password: str) -> str:
        """encrypt password for user

        Args:
            email (str): email of ther user
            password (str): password of the user

        Returns:
            str: return a hash str
        """
        assert isinstance(email, str), "Email should be a string"
        assert isinstance(password, str), "Password should be a string"

        combine_pass = email.strip() + password.strip()
        password_hash = pwd_context.hash(combine_pass)

        return password_hash

    def verify_password(self, email: str, password: str, hash_pass: str) -> bool:
        """verify the password of the user

        Args:
            email (str): email of the user
            password (str): password of ther user
            hash_pass (str): hash password

        Returns:
            bool: Return True or False
        """
        assert isinstance(email, str), "Email should be a string"
        assert isinstance(password, str), "Password should be a string"

        combine_pass = email.strip() + password.strip()
        return pwd_context.verify(combine_pass, hash_pass)
    
    @classmethod
    def verify_email(cls, email: str) -> bool:
        assert isinstance(email, str), "Email should be a string"
        """Check if an email is a verified email

        Args:
            email (str): Email of user

        Returns:
            bool: Return True or False
        """
        pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'

        return bool(re.match(pattern=pat, string=email))
    
    def create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None) -> str:
        """create an access token as JWT

        Args:
            data (dict): the data to be encoded
            expires_delta (Union[timedelta, None], optional): expired date. Defaults to None.

        Returns:
            str: a jwt token
        """        
        
        secret_key: Optional[str] = os.getenv("SECRET_KEY")
        algo: Optional[str] = os.getenv("ALGORITHM")
        
        to_encode: dict = data.copy()
        
        if expires_delta:
            expire: datetime = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        
        if secret_key and algo:
            encode_jwt: str = jwt.encode(to_encode, secret_key, algorithm=algo)
        else:
            raise EnvironmentNotFound("SECRETE_KEY and ALGORITHM")
        
        return encode_jwt
