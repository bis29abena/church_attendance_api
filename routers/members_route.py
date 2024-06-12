from sqlmodel import Session, select, column, cast, String
from db import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, Sequence, Optional, List
from dto.response import Response, SingleResponse
from entities.auth_entity.token_Entity import TokenData
from entities.members_entity import Member, MemberOutput, MemberInput, MemberInputData
from enums.enums import SuccessMessage, ErrorMessage
from routers.auth_route import get_current_active_user
from utils.user_utils import Utils
from datetime import datetime


class MembersRoute(APIRouter):
    def __init__(self) -> None:
        super().__init__(prefix="/api/membersroute")
        self.__utils = Utils()
        self.setup_routes()

    def setup_routes(self) -> None:
        self.add_api_route("/get_members", self.get_members, response_model=Response[MemberOutput], methods=["GET"])
        self.add_api_route("/get_member_byId/{memberId}", self.get_member_byId, response_model=Response[Member], methods=["GET"])
        self.add_api_route("/add_member", self.add_member, response_model=Response[Member], methods=["POST"])
        self.add_api_route("/update_member/{id}", self.update_member, response_model=Response[MemberOutput],methods=["PUT"])
        self.add_api_route("/delete_member/{id}", self.delete_member, response_model=Response[Member], methods=["DELETE"])

    async def get_members(self, current_users: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                    session: Session = Depends(get_session),
                    firstname: Optional[str] = None, lastname: Optional[str] = None, middlename: Optional[str] = None,
                    gender: Optional[str] = None, emailaddress: Optional[str] = None, phonenumber: Optional[str] = None) -> Response[MemberOutput]:
        """get all members

        Args:
            current_users (Annotated[SingleResponse[TokenData], Depends): _current_user_
            firstname (Optional[str], optional): firstname. Defaults to None.
            lastname (Optional[str], optional): lastname. Defaults to None.
            middlename (Optional[str], optional): middlename. Defaults to None.
            gender (Optional[str], optional): gender(Male/Female). Defaults to None.
            emailaddress (Optional[str], optional): emailAddress. Defaults to None.
            phonenumber (Optional[str], optional): phonenumber. Defaults to None.

        Returns:
            Response[MemberOutput]: Response of the Member Output class
        """
        response: Response[MemberOutput]

        query = select(Member)

        if firstname:
            query = query.where(column("firstname").like(f'%{firstname}%'))

        if lastname:
            query = query.where(column("lastname").like(f"%{lastname}%"))

        if middlename:
            query = query.where(column("middlename").like(f"%{middlename}%"))

        if gender:
            query = query.where(column("gender").like(f"%{gender}%"))

        if emailaddress:
            query = query.where(
                column("emailaddress").like(f"%{emailaddress}%"))
            
        if phonenumber:
            query = query.where(column("phonenumber").like(f"%{phonenumber}%"))
        
        results_list: Sequence[Member] = session.exec(query.order_by(cast(Member.createdon, String))).all()
        
        if results_list:
            results: List[MemberOutput] = [ MemberOutput(
                id = member.id,
                firstname = member.firstname,
                lastname = member.lastname,
                middlename= member.middlename,
                gender = member.gender,
                phonenumber = member.phonenumber,
                emailaddress = member.emailaddress,
                dob = member.dob,
                profile_picture = member.profile_picture,
                house_address = member.house_address,
                title_id = member.title_id
                ) for member in results_list]
            
            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = results
            )
        else:
            response = Response(
                success = False,
                message = ErrorMessage.NoEntry.value,
                data = None
            )
            
        return response
    
    async def get_member_byId(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                        memberId: int, session: Session = Depends(get_session)) -> Response[Member]:
        """get member by id

        Args:
            current_user (Annotated[SingleResponse[TokenData], Depends): current user
            memberId (int): member ID
            session (Session, optional): session. Defaults to Depends(get_session).

        Returns:
            Response[Member]: Response of member
        """  
        response: Response[Member]
        
        result: Optional[Member] = session.get(Member, memberId)   
        
        if result:
            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = result
            )
        else:
             response = Response(
                success = False,
                message = ErrorMessage.NoEntry.value,
                data = None
            ) 
              
        return response
    
    async def add_member(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)], 
                         member: MemberInput, session: Session = Depends(get_session)) -> Response[Member]:
        """add a member

        Args:
            current_user [Annotated[SingleResponse[TokenData], Depends): user
            member (MemberInputData): member
            file: file inpu
            session (Session, optional): session. Defaults to Depends(get_session).

        Returns:
            Response[Member]: Response Of Member
        """  
        response: Response[Member]
        
        if current_user:
            if current_user.success and current_user.data and current_user.data.id:
                
                member_data: MemberInputData = MemberInputData(
                    firstname = member.firstname,
                    lastname = member.lastname,
                    middlename = member.middlename,
                    emailaddress = member.emailaddress,
                    phonenumber = member.phonenumber,
                    gender = member.gender,
                    profile_picture = member.profile_picture,
                    house_address = member.house_address,
                    dob = member.dob,
                    title_id = member.title_id,
                    createdby = current_user.data.id
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
          
        new_member: Member = Member.from_orm(member_data)
        
        if new_member:

            session.add(new_member)
            session.commit()
            session.refresh(new_member)
        
            response = Response(
                success = True,
                message = SuccessMessage.MemberAdded.value,
                data = new_member
            )
        else:
            response = Response(
                success = False,
                message = ErrorMessage.MemberNotAdded.value,
                data = None
                )  
             
        return  response
    
    async def update_member(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                      id: int, new_member: MemberInput, session: Session = Depends(get_session)) -> Response[MemberOutput]:
        """update a member

        Args:
            current_user (Annotated[SingleResponse[TokenData], Depends): current_user
            id (int): id of the old user
            new_member (MemberInput): new_member
            session (Session, optional): session. Defaults to Depends(get_session).

        Returns:
            Response[MemberOutput]: Response of Member Output
        """
        response: Response[MemberOutput]
        
        old_member: Optional[Member] = session.get(Member, id)
        
        if old_member:
            if new_member.firstname:
                old_member.firstname = new_member.firstname
                
            if new_member.middlename:
                old_member.middlename = new_member.middlename
            
            if new_member.lastname:
                old_member.lastname = new_member.lastname
            
            if new_member.phonenumber:
                old_member.phonenumber = new_member.phonenumber
            
            if new_member.gender:
                old_member.gender = new_member.gender
                
            if new_member.profile_picture:
                old_member.profile_picture = new_member.profile_picture
                
            if new_member.dob:
                old_member.dob = new_member.dob
            
            if new_member.house_address:
                old_member.house_address = new_member.house_address
                
            if new_member.emailaddress:
                if not self.__utils.verify_email(new_member.emailaddress):
                    return Response(success=False, message=ErrorMessage.InvalidEmail.value, data = None)
                
                old_member.emailaddress = new_member.emailaddress
                
            if current_user.success and current_user.data and current_user.data.id:
                old_member.modifiedby = current_user.data.id
                
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            old_member.modifiedon = datetime.utcnow()
            
            session.commit()
            session.refresh(old_member)
            
            result: MemberOutput = MemberOutput(
                id = old_member.id,
                firsname = old_member.firstname,
                lastname = old_member.lastname,
                middlename = old_member.middlename,
                gender = old_member.gender,
                phonenumber = old_member.phonenumber,
                emailaddress = old_member.emailaddress,
                profile_picture = old_member.profile_picture,
                title_id = old_member.title_id,
                house_address = old_member.house_address,
                dob = old_member.dob
            )
            
            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = result
            )
            
        else:
            response = Response(
                success=False,
                message=ErrorMessage.NoEntry.value,
                data=None
            )
            
        return response
    
    async def delete_member(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                      id: int, session: Session = Depends(get_session)) -> Response[Member]:
        """Delete member

        Args:
            current_user (Annotated[SingleResponse[TokenData], Depends): current user
            id (int): id of the user
            session (Session, optional): Session. Defaults to Depends(get_session).

        Returns:
            Response[Member]: Response of the user
        """ 
        response: Response[Member]
        
        member: Optional[Member] = session.get(Member, id)
        
        if member:
            session.delete(member)
            session.commit()
            
            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = member
            )
        else:
            response = Response(
                success = False,
                message = ErrorMessage.NoEntry.value,
                data = None
            )
            
        return response          
    