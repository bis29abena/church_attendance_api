from fastapi import APIRouter, Depends
from typing import Sequence, Tuple, Annotated
from sqlmodel import Session, select, cast, String, column
from db import get_session
from typing import Optional
from enums.enums import SuccessMessage, ErrorMessage
from dto.response import Response, SingleResponse
from entities.service_type_enity import ServiceType, ServiceTypeInput, ServiceTypeUser
from entities.user_entity import User
from entities.auth_entity.token_Entity import TokenData
from routers.auth_route import AuthRouter, get_current_active_user
from datetime import datetime


class ServiceTypeRouter(APIRouter):
    def __init__(self):
        super().__init__(prefix="/api/servicetype")
        self.setup_routes()

    def setup_routes(self) -> None:
        self.add_api_route("/getservicetypes", endpoint=self.get_serivcetypes,
                           methods=["GET"])
        self.add_api_route("/getservicebyid/{id}", endpoint=self.get_servicetypeby_id, methods=[
                           "GET"], response_model=Response[ServiceTypeUser])
        self.add_api_route("/addservicetype", endpoint=self.add_servicetype,
                           methods=["POST"], response_model=Response[ServiceType])
        self.add_api_route("/updateservicetype", methods=[
                           "PUT"], endpoint=self.change_servicetype, response_model=Response[ServiceType])
        self.add_api_route("/deleteservicetype", methods=[
                           "DELETE"], endpoint=self.remove_servicetype, response_model=Response[ServiceType])

    async def get_serivcetypes(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                               name: Optional[str] = None, 
                               session: Session = Depends(get_session)) -> Response[ServiceTypeUser]:
        """get all services

        Args:
            name (Optional[str], optional): filter by name Defaults to None.
            session (Session, optional): dependency. Defaults to Depends(get_session).

        Returns:
            Response[ServiceTypeUser]: get all service type with it's corresponding user
        """
        
        response: Response[ServiceTypeUser] 

        query = select(ServiceType, User).join(User)

        if name:
            query = query.where(column("name").like(f"%{name}%"))

        result_db: Sequence[Tuple[ServiceType, User]] = session.exec(query.order_by(cast(ServiceType.createdon, String))).all()
        
        if result_db:

            servicetypeuserslist: list[ServiceTypeUser] = [ServiceTypeUser(
                id=servicetype.id,
                name=servicetype.name,
                createdby=user.emailaddress,
                modifiedby=user.emailaddress if servicetype.modifiedon is not None else servicetype.modifiedon,
                createdon=servicetype.createdon,
                modifiedon=servicetype.modifiedon
            ) for servicetype, user in result_db]

            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = servicetypeuserslist
            )
            

        else:
            response = Response(
                success=False, 
                message=ErrorMessage.NoEntry.value, 
                data=None
            )

        return response

    async def get_servicetypeby_id(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                                   id: int, 
                                   session: Session = Depends(get_session)) -> Response[ServiceTypeUser]:
        """get service type by id

        Args:
            id (int): id of the of the service type
            session (Session, optional): dependency. Defaults to Depends(get_session).

        Returns:
            Response[ServiceTypeUser]: Return a respone of ServiceTypeUser
        """
        servicetypeUser: ServiceTypeUser
        response: Response[ServiceTypeUser]

        result: Optional[Tuple[ServiceType, User]] = session.exec(select(ServiceType, User).join(
            User).where(ServiceType.id == id)).first()

        if result:

            servicetypeUser = ServiceTypeUser(
                id = result[0].id,
                name = result[0].name,
                createdby = result[1].emailaddress,
                modifiedby = result[1].emailaddress if result[0].modifiedby else None,
                createdon = result[0].createdon,
                modifiedon = result[0].modifiedon
            )
            
            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = servicetypeUser
            )


        else:
            response = Response(
                success = False,
                message = ErrorMessage.NoEntry.value,
                data = servicetypeUser
            )
           

        return response

    async def add_servicetype(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                              serviceData: ServiceTypeInput, 
                              session: Session = Depends(get_session)) -> Response[ServiceType]:
        """Add a service type

        Args:
            serviceData (ServiceTypeInput): service data
            session (Session, optional): _description_. Defaults to Depends(get_session).

        Returns:
            Response[ServiceType]: _description_
        """
        response: Response[ServiceType]

        # check if serviceType Already Exist
       
        serviceTypeExist: Optional[ServiceType] = session.exec(select(ServiceType).where(
            ServiceType.name == serviceData.name)).first()

        if serviceTypeExist:
            
            response = Response(
                success = False,
                message = ErrorMessage.ServiceTypeExists.value,
                data = None
            )
            

            return response

        servicetype = ServiceType.from_orm(serviceData)

        if servicetype:
            
            if current_user.success and current_user.data and current_user.data.id:
                servicetype.createdby = current_user.data.id
                
            session.add(servicetype)
            session.commit()
            session.refresh(servicetype)

            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = servicetype
            )
            
        else:
            response = Response(
                success=False, 
                message=ErrorMessage.ServiceTypeNotAdded.value, 
                data=servicetype
            )

        return response

    async def change_servicetype(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                                 id: int, 
                                 new_serviceType: ServiceTypeInput, 
                                 sesion: Session = Depends(get_session)) -> Response[ServiceType]:
        """update response type

        Args:
            id (int): id of the service Type to update
            new_serviceType (ServiceTypeInput): data for the new service type
            sesion (Session, optional): dependency. Defaults to Depends(get_session).

        Returns:
            Response[ServiceType]: Return a response type
        """
        response: Response[ServiceType]

        if (data_found := sesion.exec(select(ServiceType).where(ServiceType.name == new_serviceType.name)).first()):
            
            response = Response(
                success = False,
                message = ErrorMessage.ServiceTypeExists.value,
                data = data_found
            )
            

            return response

        old_data: Optional[ServiceType] = sesion.get(ServiceType, id)

        if current_user.success and current_user.data:
            if old_data:
                old_data.name = new_serviceType.name
                old_data.modifiedby = current_user.data.id
                old_data.modifiedon = datetime.utcnow()

                sesion.add(old_data)
                sesion.commit()
                sesion.refresh(old_data)

                response = Response(
                    success = True,
                    message = SuccessMessage.OperationSuccessful.value,
                    data = old_data
                )
            
            else:
                response = Response(success=False, message=ErrorMessage.NoEntry.value, data=old_data)

        return response

    async def remove_servicetype(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                                 id: int, 
                                 session: Session = Depends(get_session)) -> Response[ServiceType]:
        """delete a service type

        Args:
            id (int): id of the service type to delete
            session (Session, optional): Depends. Defaults to Depends(get_session).

        Returns:
            Response[ServiceType]: Response Type of the deleted item
        """
        response: Response[ServiceType]

        del_item: Optional[ServiceType] = session.get(ServiceType, id)

        if del_item:
            session.delete(del_item)
            session.commit()

            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = del_item
            )
            
        else:
            response = Response(success=False, message=ErrorMessage.NoEntry.value, data=del_item)

        return response
