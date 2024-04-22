from fastapi import APIRouter, Depends
from sqlmodel import Session, select, cast, String, column
from db import get_session
from entities.user_entity import User, UserInput, UserOutput, UserFilter
from dto.response import Response
from datetime import datetime
from enums.enums import SuccessMessage, ErrorMessage
from utils.utils import Utils
from typing import Optional, Sequence
import os
from exceptions.env_exceptions import EnvironmentNotFound


class UserRouter(APIRouter):
    def __init__(self):
        super().__init__(prefix="/api/user")
        self.setup_routes()
        self.__utils = Utils()

    def setup_routes(self) -> None:
        self.add_api_route("/get_users", self.get_users,
                           methods=["POST"], response_model=Response[UserOutput])
        self.add_api_route("/add_user", self.add_user,
                           methods=["POST"], response_model=Response[UserOutput])
        self.add_api_route("/update_user/{id}", self.update_user,
                           methods=["PUT"], response_model=Response[UserOutput])
        self.add_api_route("/delete_user/{id}", self.delete_user,
                           methods=["DELETE"], response_model=Response[UserOutput])
        self.add_api_route("/enable_disable/{id}", self.enable_disable_user, methods=[
                           "PUT"], response_model=Response[UserOutput])
        self.add_api_route("/forgotten_password", self.forgotten_password,
                           methods=["PUT"], response_model=Response[UserOutput])
        self.add_api_route("/reset_password/{id}", self.reset_password, methods=["PUT"],
                           response_model=Response[UserOutput])

    async def get_users(self, firstname: Optional[str] = None, middlename: Optional[str] = None,
                        lastname: Optional[str] = None, emailaddress: Optional[str] = None,
                        phoneNumber: Optional[str] = None, session: Session = Depends(get_session)) -> Response[UserOutput]:
        """Get all Users

        Args:
            user (UserFilter): user filter to get what is required
            session (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[UserOutput]: Out a list of Users
        """
        response: Response[UserOutput]

        query = select(User)

        if firstname:
            query = query.where(column("firstname").like(f"%{firstname}%"))
        if middlename:
            query = query.where(column("middlename").like(f"%{middlename}%"))
        if lastname:
            query = query.where(column("lastname").like(f"%{lastname}%"))
        if emailaddress:
            query = query.where(User.emailaddress == emailaddress)
        if phoneNumber:
            query = query.where(User.phoneNumber == phoneNumber)

        result: Sequence[User] = session.exec(query.order_by(
            cast(User.createdon, String))).all()

        if result:
            user_output_list: list[UserOutput] = [
                UserOutput(
                    id = user.id,
                    firstname=user.firstname,
                    middlename=user.middlename,
                    lastname=user.lastname,
                    gender=user.gender,
                    phoneNumber= user.phoneNumber,
                    emailaddress=user.emailaddress,
                    disabled=user.disabled,
                    createdon=user.createdon,
                    modifiedon=user.modifiedon
                )
                
                for user in result
            ]
            response = Response(
                success=True,
                message=SuccessMessage.OperationSuccessful.value,
                data=user_output_list
            )
        else:
            response = Response(
                success=False,
                message=ErrorMessage.NoEntry.value,
                data=None
            )

        return response

    async def add_user(self, user: UserInput, sesssion: Session = Depends(get_session)) -> Response[UserInput]:
        """Add a new user to the table

        Args:
            user (UserInput): user details from the user
            sesssion (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[UserInput]: Return a response of the new created user
        """
        response: Response[UserInput]

        if user.emailaddress:
            if not self.__utils.verify_email(user.emailaddress):

                response = Response(
                    success=False,
                    message=ErrorMessage.InvalidEmail.value,
                    data=None
                )

                return response

        new_user: User = User.from_orm(user)

        if new_user:
            # encrypt the user password
            hashpass = self.__utils.encrypt_password(
                new_user.emailaddress, new_user.password)
            # replace the user password
            new_user.password = hashpass
            sesssion.add(new_user)
            sesssion.commit()
            sesssion.refresh(new_user)

            response = Response(
                success=True,
                message=SuccessMessage.OperationSuccessful.value,
                data=new_user
            )
        else:
            response = Response(
                success=True,
                message=ErrorMessage.UserNotAdded.value,
                data=None
            )

        return response

    async def update_user(self, id: int, user: UserFilter, session: Session = Depends(get_session)) -> Response[UserOutput]:
        """Update user details

        Args:
            id (int): ID of the data to be updated
            user (UserFilter): Details of the new data
            session (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[UserOutput]: Return a response of the new data to be created
        """
        response: Response[UserOutput]

        if user.emailaddress:
            if not self.__utils.verify_email(user.emailaddress):
                response = Response(
                    success=False,
                    message=ErrorMessage.InvalidEmail.value,
                    data=None
                )

                return response

        old_user: Optional[User] = session.get(User, id)

        if old_user:
            if user.firstname:
                old_user.firstname = user.firstname
            if user.middlename:
                old_user.middlename = user.middlename
            if user.lastname:
                old_user.lastname = user.lastname
            if user.emailaddress:
                
                # verify the email address
                if not self.__utils.verify_email(user.emailaddress):
                    response = Response(
                        success=False,
                        message=ErrorMessage.InvalidEmail.value,
                        data=None
                    )

                    return response
                
                old_user.emailaddress = user.emailaddress
            if user.phoneNumber:
                old_user.phoneNumber = user.phoneNumber
            if user.disabled:
                old_user.disabled = user.disabled
            if user.gender:
                old_user.gender = user.gender
                
            old_user.modifiedon = datetime.utcnow()

            session.commit()
            session.refresh(old_user)

            updated_user: UserOutput = UserOutput(
                id=old_user.id,
                firtname=old_user.firstname,
                lastname=old_user.lastname,
                middlename=old_user.middlename,
                emailaddress=old_user.emailaddress,
                phoneNumber=old_user.phoneNumber,
                gender=old_user.gender,
                disabled=old_user.disabled
            )
            
            response = Response(
                success=True,
                message=SuccessMessage.UserUpdated.value,
                data=updated_user
            )
        else:
            response = Response(
                success=True,
                message=ErrorMessage.UserNotFound.value,
                data=None
            )
        return response

    async def delete_user(self, id: int, sesssion: Session = Depends(get_session)) -> Response[UserOutput]:
        """A user to be deleted

        Args:
            id (int): Id of the user to be deleted
            sesssion (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[UserOutput]: Return a response of the data to be deleted
        """
        response: Response[UserOutput]

        user: Optional[User] = sesssion.get(User, id)

        if user:
            sesssion.delete(user)
            sesssion.commit()

            user_output: UserOutput = UserOutput(
                id=user.id,
                firstname=user.firstname,
                lastname=user.lastname,
                middlename=user.middlename,
                gender=user.gender,
                emailaddress=user.emailaddress,
                phoneNumber=user.phoneNumber,
                disabled=user.disabled
            )
            response = Response(
                success=True,
                message=SuccessMessage.UserRemoved.value,
                data=user_output
            )
        else:
            response = Response(
                success=True,
                message=ErrorMessage.UserNotAdded.value,
                data=None
            )

        return response

    async def enable_disable_user(self, id: int, session: Session = Depends(get_session)) -> Response[UserOutput]:
        """Enable or Disable a user

        Args:
            id (int): ID of the user to be enabled
            session (Session, optional): _description_. Defaults to Depends(get_session).

        Returns:
            Response[UserOutput]: Return a response of the user enabled or disabled
        """
        response: Response[UserOutput]

        user: Optional[User] = session.get(User, id)
        message: str

        if user:
            if user.disabled:
                message = SuccessMessage.UserDisabled.value
            else:
                message = SuccessMessage.UserEnabled.value

            user.disabled = not user.disabled
            user.modifiedon = datetime.utcnow()

            session.commit()
            session.refresh(user)
            
            user_output: UserOutput = UserOutput(
                id=user.id,
                firstname=user.firstname,
                lastname=user.lastname,
                middlename=user.middlename,
                gender=user.gender,
                emailaddress=user.emailaddress,
                phoneNumber=user.phoneNumber,
                disabled=user.disabled
            )

            response = Response(
                success=True,
                message=message,
                data=user_output
            )
        else:
            response = Response(
                success=True,
                message=ErrorMessage.UserNotFound.value,
                data=None
            )
        return response

    async def forgotten_password(self, email: str, new_password: str, session: Session = Depends(get_session)) -> Response[UserOutput]:
        """Reset user password

        Args:
            email (str): Email of the user
            new_password (str): New password of the user
            session (Session, optional): _description_. Defaults to Depends(get_session).

        Returns:
            Response[UserOutput]: Return a response of the user reseted
        """
        response: Response[UserOutput]
        
        if email:
            if not self.__utils.verify_email(email):
                response = Response(
                    success=False,
                    message=ErrorMessage.InvalidEmail.value,
                    data=None
                )

                return response

        result: User = session.exec(select(User).where(
            User.emailaddress == email)).one()

        if result:
            result.password = self.__utils.encrypt_password(
                email, new_password)
            result.modifiedon = datetime.utcnow()

            session.commit()
            session.refresh(result)

            user_output: UserOutput = UserOutput(
                id=result.id,
                firstname=result.firstname,
                lastname=result.lastname,
                middlename=result.middlename,
                gender=result.gender,
                emailaddress=result.emailaddress,
                phoneNumber=result.phoneNumber,
                disabled=result.disabled
            )
            
            response = Response(
                success=True,
                message=SuccessMessage.UserResetPassword.value,
                data=user_output
            )
        else:
            response = Response(
                success=True,
                message=ErrorMessage.UserNotFound.value,
                data=None
            )
        return response

    async def reset_password(self, id: int, session: Session = Depends(get_session)) -> Response[UserOutput]:
        """Reset the password of the user

        Args:
            id (int): id of the user
            session (Session, optional): dependency. Defaults to Depends(get_session).

        Returns:
            Response[UserOutput]: Return the user 
        """
        response: Response[UserOutput]
        
        password_reset: Optional[str] = os.getenv("RESET_PASSWORD")
        
        if password_reset:
            
            # get the user using the id
            user: Optional[User] = session.get(User, id)
            
            if user:
                
                # update the user password with the reset password
                user.password = self.__utils.encrypt_password(user.emailaddress, password_reset)
                user.modifiedon = datetime.utcnow()
                
                session.commit()
                session.refresh(user)
                
                user_output: UserOutput = UserOutput(
                    id=user.id,
                    firstname=user.firstname,
                    lastname=user.lastname,
                    middlename=user.middlename,
                    gender=user.gender,
                    phoneNumber=user.phoneNumber,
                    emailaddress=user.emailaddress,
                    createdon=user.createdon,
                    modifiedon=user.modifiedon
                )
                
                response = Response(
                    success=True,
                    message=SuccessMessage.OperationSuccessful.value,
                    data=user_output
                )
            else:
                response = Response(
                    success=False,
                    message=ErrorMessage.NoEntry.value,
                    data=None
                )
        else:
            raise EnvironmentNotFound("RESET_PASSWORD")
        
        return response