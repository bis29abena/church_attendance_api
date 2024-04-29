from fastapi import APIRouter, Depends
from entities.attendance_type_entity import AttendanceType, AttendanceTypeInput, AttendanceTypeOutput, AttendanceTypeUser
from entities.user_entity import User
from entities.auth_entity.token_Entity import TokenData
from db import get_session
from sqlmodel import Session, select, cast, String, column
from dto.response import Response, SingleResponse
from typing import Optional, Sequence, Annotated
from enums.enums import SuccessMessage, ErrorMessage
from datetime import datetime
from routers.auth_route import AuthRouter, get_current_active_user


class AttendancetypeRouter(APIRouter):
    def __init__(self):
        super().__init__(prefix="/api/attendancetype")
        self.setup_routes()

    def setup_routes(self) -> None:
        self.add_api_route(path="/getAll", endpoint=self.get_attendancetypes,
                           methods=["GET"], response_model=Response[AttendanceTypeUser])
        self.add_api_route(path="/getbyId/{title_id}", endpoint=self.get_attendanceType_id,
                           methods=["GET"], response_model=Response[AttendanceType])
        self.add_api_route(path="/addattendacetype", endpoint=self.add_attendanceType,
                           methods=["POST"], response_model=Response[AttendanceType])
        self.add_api_route(path="/updateattendancetype/{id}", methods=[
                           "PUT"], endpoint=self.change_attendancetype, response_model=Response[AttendanceType])
        self.add_api_route(path="/deleteattendancetype/{id}", methods=[
                           "DELETE"], endpoint=self.remove_attendacetype, response_model=Response[AttendanceTypeOutput])

    async def get_attendancetypes(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                                  name: Optional[str] = None, 
                                  session: Session = Depends(get_session),
                                  ) -> Response[AttendanceTypeUser]:
        """Get All attendance type in the church

        Args:
            name (Optional[str], optional): if name is specified. Defaults to None.
            session (Session, optional): dependency. Defaults to Depends(get_session).

        Returns:
            Reponse[AttendanceTypeOutPut]: Return a response of the AttendaceType Output Model
        """
        query = select(AttendanceType, User).join(User)
        response: Response[AttendanceTypeUser]

        if name:
            query = query.where(column("name").like(f"%{name}%"))
            
        result_db: Sequence[tuple[AttendanceType, User]] = session.exec(query.order_by(
            cast(AttendanceType.createdon, String))).all()

        attendanceOutputList: list[AttendanceTypeUser] = []

        for attendance, user in result_db:
            at_user: AttendanceTypeUser = AttendanceTypeUser(
                id=attendance.id,
                name=attendance.name,
                email_createdby=user.emailaddress,
                email_modifiedby=user.emailaddress if attendance.modifiedby else attendance.modifiedby,
                createdon=attendance.createdon,
                modifiedon=attendance.modifiedon
            )

            attendanceOutputList.append(at_user)

        if attendanceOutputList:
            response = Response(
                success=True,
                message=SuccessMessage.OperationSuccessful.value,
                data=attendanceOutputList
            )
        else:
            return Response(success=False, message=ErrorMessage.NoAttendanceFound.value, data=None)

        return response

    async def get_attendanceType_id(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                                    id: int, 
                                    session: Session = Depends(get_session)) -> Response[AttendanceType]:
        """get attendace by ID

        Args:
            id (int): Title ID
            session (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[AttendanceType]: Return a reponse of AttendanceType
        """
        title: Optional[AttendanceType] = session.get(AttendanceType, id)

        response = None

        if title:
            response = Response(
                success=True,
                message=SuccessMessage.OperationSuccessful.value,
                data=title
            )

        else:
            return Response(
                success=False,
                message=ErrorMessage.NoAttendanceFound.value,
                data=title
            )
        return response

    async def add_attendanceType(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                                 attendancetype: AttendanceTypeInput, 
                                 session: Session = Depends(get_session)) -> Response[AttendanceType]:
        """Add new attendanceType to the table

        Args:
            attendancetype (AttendanceTypeInput): attendanceType data to be added
            session (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[Title]: Return a reponse of the AttendanceTypeOutput Created
        """
        response: Response[AttendanceType]

        attendance_search: Sequence[AttendanceType] = session.exec(select(AttendanceType).where(
            AttendanceType.name == attendancetype.name)).all()

        if attendance_search:
            response = Response(
                success=False,
                message=ErrorMessage.AttendaceTypeAlreadyExist.value,
                data=attendance_search[0]
            )

            return response

        new_attendanceType: AttendanceType = AttendanceType.from_orm(attendancetype)
        
        if current_user.success and current_user.data and current_user.data.id:
            new_attendanceType.createdby = current_user.data.id
            
        session.add(new_attendanceType)
        session.commit()
        session.refresh(new_attendanceType)
        if new_attendanceType:
            response = Response(
                success=True,
                message=SuccessMessage.AttendanceTypeAdded.value,
                data=new_attendanceType,
            )
        else:
            return Response(success=True, message=ErrorMessage.AttendaceTypeNotAdded.value, data=new_attendanceType)

        return response

    async def change_attendancetype(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                                    id: int, 
                                    new_attendanceType: AttendanceTypeInput, 
                                    session: Session = Depends(get_session)) -> Response[AttendanceType]:
        """Update AttendanceType

        Args:
            id (int): Id of the old Title
            new_attendanceType (AttendanceTypeInput): Data for the new attendance Type
            session (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[AttendanceTypeOutput]: Return a response of Title OutPut
        """
        response: Response[AttendanceType]

        attendance_search: Sequence[AttendanceType] = session.exec(select(AttendanceType).where(
            AttendanceType.name == new_attendanceType.name)).all()

        if attendance_search:
            response = Response(
                success=False,
                message=ErrorMessage.AttendaceTypeAlreadyExist.value,
                data=attendance_search[0]
            )

            return response

        old_attendanceType: Optional[AttendanceType] = session.get(AttendanceType, id)
        
        if current_user.success and current_user.data:

            if old_attendanceType:
                old_attendanceType.name = new_attendanceType.name
                old_attendanceType.modifiedby = current_user.data.id
                old_attendanceType.modifiedon = datetime.utcnow()
                session.commit()
                session.refresh(old_attendanceType)

                response = Response(
                    success=True,
                    message=SuccessMessage.OperationSuccessful.value,
                    data=old_attendanceType
                )
            else:

                response = Response(
                    success=False,
                    message=ErrorMessage.AttendanceTypeNotUpdated.value,
                    data=old_attendanceType
                )
        return response

    async def remove_attendacetype(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                                   id: int, 
                                   session: Session = Depends(get_session)) -> Response[AttendanceType]:
        """Remove an Attendance Type

        Args:
            id (int): Id of the item to remove
            session (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[AttendanceType Output]: Reponse Object of the AttendanceType to remove
        """
        response: Response[AttendanceType]

        attendanceType_del: Optional[AttendanceType] = session.get(AttendanceType, id)

        if attendanceType_del:
            session.delete(attendanceType_del)
            session.commit()

            response = Response(
                success=True,
                message=SuccessMessage.AttendanceTypeRemoved.value,
                data=attendanceType_del
            )

        else:
            response = Response(
                success=True,
                message=ErrorMessage.NoAttendanceFound.value,
                data=attendanceType_del
            )
        return response
