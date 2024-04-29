from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta
from typing import Optional, Annotated
from entities.user_entity import User
from entities.auth_entity.token_Entity import Token, TokenData, TokenDataExp
from dto.response import SingleResponse
from utils.user_utils import Utils
from exceptions.env_exceptions import EnvironmentNotFound
from enums.enums import SuccessMessage, ErrorMessage
from sqlmodel import Session, select
from db import get_session_funct

import os


oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")



class AuthRouter(APIRouter):
    def __init__(self)->None:
        super().__init__()
        self.setup_routes()
        self.__utils: Utils = Utils()
        
    def setup_routes(self):
        self.add_api_route("/token", self.login, methods=["POST"], response_model=Token)
        
    async def __authenticateUser(self, email: str, password: str) -> User | bool:
        """authenticate a user

        Args:
            email (str): email of the user
            password (str): password of the user

        Returns:
            User | bool: Return the user or a bool
        """        
        
        res: User
        
        # get user using the username
        user: SingleResponse[User] = await self.get_user_by_email(email) 
        
        if not user.success:
            return False
        
        if user.data:
            
            if not self.__utils.verify_password(email=email, password=password, hash_pass = user.data.password):
                return False
            
            res = user.data
        
        return res
    
    @classmethod
    async def get_current_user(cls, token: Annotated[str, Depends(oauth2_scheme)]) -> SingleResponse[User]:
        """get current user

        Args:
            token (Annotated[str, Depends): token

        Raises:
            credentials_exception: raise exception if credentials is invalid
            EnvironmentNotFound: raise exception if environment variables is not found
            credentials_exception: raise exception if credentials is invalid

        Returns:
            SingleResponse[User]: Return a single user
        """        
        
        credentials_exception: HTTPException = HTTPException(
                                                    status_code=status.HTTP_401_UNAUTHORIZED,
                                                    detail="Could not validate credentials",
                                                    headers={"WWW-Authenticate": "Bearer"},
                                                )
        
        secrete_key: Optional[str] = os.getenv("SECRET_KEY")
        algo: Optional[str] = os.getenv("ALGORITHM")
        
        res: SingleResponse[User]
        token_data: TokenDataExp
        
        try:
            if secrete_key and algo:
                payload = jwt.decode(token=token, key=secrete_key, algorithms=[algo])

                user_data: Optional[TokenDataExp] = TokenDataExp(**payload)
                
                if user_data is None:
                    raise credentials_exception
                else:
                    token_data = user_data
                
            else:
                raise EnvironmentNotFound("SECRET_KEY and ALGORITHM")
        except JWTError:
            raise credentials_exception
        
        email: Optional[str] = token_data.emailAddress
        
        if email:
            user: SingleResponse[User] = await cls.get_user_by_email(email=email)
            
        if user.success and user.data:
            res = user
            
        return res
    
    
    async def login(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
        """login to get access token

        Args:
            form_data (Annotated[OAuth2PasswordRequestForm, Depends): form data from user

        Raises:
            HTTPException: raise an http exception
            EnvironmentNotFound: raise an environment variable not found

        Returns:
            Token: Return Token
        """        
        user: User | bool = await self.__authenticateUser(email=form_data.username, password=form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_time: Optional[str] = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTE")
        
        if access_token_time:
            time_expire: int = int(access_token_time)
            
            access_token_expires = timedelta(minutes=time_expire)
            
        else:
            raise EnvironmentNotFound("ACCESS_TOKEN_EXPIRE_MINUTE")
        
        if isinstance(user, User):
            access_token = self.__utils.create_access_token({"id": user.id, "emailAddress": user.emailaddress}, access_token_expires)
            
        return Token(access_token=access_token, token_type="bearer")
    
    @classmethod
    async def get_user_by_email(cls, email: str) -> SingleResponse[User]:
        """get a user by email

        Args:
            email (str): email address of the user
            session (Session, optional): dependency. Defaults to Depends(get_session).

        Returns:
            Response[User]: returns a reponse of the user
        """
        session: Session = get_session_funct()
        
        response: SingleResponse[User]
        
        if email:
            
            if not Utils.verify_email(email=email):
                response = SingleResponse(
                    success=False,
                    message=ErrorMessage.InvalidEmail.value,
                    data=None
                )    
                
                return response
            
            user: Optional[User] =  session.exec(select(User).where(User.emailaddress == email)).one()
            
            if user: 
            
                response = SingleResponse(
                    success=True,
                    message=SuccessMessage.OperationSuccessful.value,
                    data=user
                )
            else:
                response = SingleResponse(
                    success=False,
                    message=ErrorMessage.UserNotFound.value,
                    data=None
                )
                
        return response
    


async def get_current_active_user(current_user: Annotated[SingleResponse[User], Depends(AuthRouter.get_current_user)]) -> SingleResponse[TokenData]:
    """get active user

    Args:
        current_user (Annotated[SingleResponse[User], Depends): current user

    Raises:
        HTTPException: raise an exception if user is inactive
        HTTPException: raise an exception if user is not found

    Returns:
        User: Return user
    """
    response: SingleResponse[TokenData]     
    
    if current_user.success and current_user.data:
        if current_user.data.disabled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    token_data: TokenData = TokenData(
        id = current_user.data.id,
        emailAddress = current_user.data.emailaddress
    )
    response = SingleResponse(
        success=True,
        message=SuccessMessage.UserFound.value,
        data=token_data
    )
    
    return response