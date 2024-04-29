from fastapi import APIRouter, Depends
from typing import List, Tuple, Optional, Sequence, Annotated
from sqlmodel import Session, select, cast, String, column, join
from db import get_session
from dto.response import Response, SingleResponse
from datetime import date, time, datetime
from entities.service_entity import Service, ServiceAndServiceTypeAndUserOutput, ServiceInput, ServiceOutput
from entities.service_type_enity import ServiceType
from entities.user_entity import User
from entities.auth_entity.token_Entity import TokenData
from enums.enums import SuccessMessage, ErrorMessage
from routers.auth_route import AuthRouter, get_current_active_user



class ServiceRoute(APIRouter):
    def __init__(self):
        super().__init__(prefix="/api/service")
        self.setup_routes()
        
    def setup_routes(self) -> None:
        self.add_api_route(path="/getservices", endpoint=self.get_services, methods=["GET"], response_model=Response[ServiceAndServiceTypeAndUserOutput])
        self.add_api_route(path="/getservicebyid/{id}", endpoint=self.get_service_byId, methods=["GET"], response_model=Response[ServiceAndServiceTypeAndUserOutput])
        self.add_api_route(path="/addservice", endpoint=self.add_service, methods=["POST"], response_model=Response[ServiceOutput])
        self.add_api_route(path="/updateservice/{id}", endpoint=self.update_service,methods=["PUT"], response_model=Response[ServiceOutput])
        self.add_api_route(path="/deleteservice/{id}", endpoint=self.delete_service, methods=["DELETE"], response_model=Response[Service])
        
    async def get_services(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                           servicetypeid: Optional[int] = None, location: Optional[str] = None, date_event: Optional[date] = None,
                           time_start: Optional[time] = None, session: Session = Depends(get_session)) -> Response[ServiceAndServiceTypeAndUserOutput]:
        """_summary_

        Args:
            serviceid (Optional[id], optional): servicetypeid. Defaults to None.
            location (Optional[str], optional): location of the service. Defaults to None.
            date_event (Optional[date], optional): date of the service. Defaults to None.
            time_start (Optional[time], optional): time of the service. Defaults to None.
            session (Session, optional): _description_. Defaults to Depends(get_session).

        Returns:
            Response[ServiceAndServiceTypeAndUserOutput]: _description_
        """        
        
        response: Response[ServiceAndServiceTypeAndUserOutput] 
        

        # Assuming Service, ServiceType, and User are table objects
        query = (
                select(Service, ServiceType, User).select_from(join(Service, ServiceType, Service.servicetypeId == ServiceType.id).join(User, User.id == Service.createdby) # type: ignore # this conditonal clause cannot be defined
                )
            )
        
        # filter the query
        if servicetypeid:
            query = query.where(ServiceType.id == servicetypeid) 
        
        if location:
            query = query.where(column("location").like(f"%{location}%"))
        
        if date_event:
            query = query.where(Service.date_event == date_event)
        
        if time_start:
            query = query.where(Service.time_start == time_start)
        
        # get the result from the query and order by 
        result_db: Sequence[Tuple[Service, ServiceType, User]] = session.exec(query.order_by(cast(Service.createdon, String))).all()
        
        if result_db:
            
            outputlist: List[ServiceAndServiceTypeAndUserOutput] = [ServiceAndServiceTypeAndUserOutput(
                id=service.id,
                servicename=servicetype.name,
                date_event=service.date_event,
                time_start=service.time_start,
                location=service.location,
                createdby=user.emailaddress,
                modifiedby= user.emailaddress if service.modifiedon is not None else service.modifiedon,
                createdon=service.createdon,
                modifiedon= service.modifiedon
            ) for service, servicetype, user in result_db ]

            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = outputlist
            )
            
        else:
            return Response(success = False, message = ErrorMessage.NoEntry.value, data = None)
            
        return response
    
    async def get_service_byId(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                               id: int, 
                               session: Session = Depends(get_session)) -> Response[ServiceAndServiceTypeAndUserOutput]:
        """get service by id

        Args:
            id (int): id of the service
            session (Session, optional): dependency. Defaults to Depends(get_session).

        Returns:
            Response[ServiceAndServiceTypeAndUserOutput]: return the service.
        
        """        
        
        serviceUser: ServiceAndServiceTypeAndUserOutput 
        
        response: Response[ServiceAndServiceTypeAndUserOutput] 
        
        result: Optional[Tuple[Service, ServiceType, User]] = session.exec(select(Service, ServiceType, User).select_from(join(Service, ServiceType, Service.servicetypeId == ServiceType.id).join(User, User.id == Service.createdby) # type: ignore # this conditonal clause cannot be defined
                )).first()
        
        if result:
            
            serviceUser = ServiceAndServiceTypeAndUserOutput(
                id = result[0].id,
                servicename = result[1].name,
                location = result[0].location,
                date_event = result[0].date_event,
                time_start = result[0].time_start,
                createdby = result[2].emailaddress,
                modifiedby = result[2].emailaddress if result[0].modifiedby is not None else result[0].modifiedby, 
                createdon = result[0].createdon,
                modifiedon = result[0].modifiedon
            )
            
            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = serviceUser
            )
            
        
        else:
            response = Response(
                success = False,
                message = ErrorMessage.NoEntry.value,
                data = None
            )
        
        return response
    
    async def add_service(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                          service: ServiceInput, 
                          session: Session = Depends(get_session)) -> Response[Service]:
        """add a service

        Args:
            service (ServiceInput): service input
            session (Session, optional): depedency. Defaults to Depends(get_session).

        Returns:
            Response[ServiceOutput]: returns the service created
        """
        
        response: Response[Service] 
        
        added_service: Service = Service.from_orm(service)
        
        if added_service:
            
            # check if there is a user
            if current_user.success and current_user.data and current_user.data.id:
                added_service.createdby = current_user.data.id
                
            session.add(added_service)
            session.commit()
            session.refresh(added_service)
            
            response = Response(
                success = True,
                message = SuccessMessage.ServiceAdded.value,
                data = added_service
            )
            
        else:
            response = Response(
                success = False,
                message = ErrorMessage.ServiceNotAdded.value,
                data = None
            )
        
        return response
    
    async def update_service(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                             id: int, 
                             service: ServiceInput, session: Session = Depends(get_session)) -> Response[Service]:
        """Update a service

        Args:
            id (int): id of the service
            service (ServiceInput): new data of the service 
            session (Session, optional): dependency. Defaults to Depends(get_session).

        Returns:
            Response[ServiceOutput]: return a reponse of the service updated
        """
        
        response: Response[Service]
        
        old_service: Optional[Service] = session.get(Service, id)
        
        if current_user.success and current_user.data:
            if old_service:
                
                if service.servicetypeId:
                    old_service.servicetypeId = service.servicetypeId
                    
                if service.location:
                    old_service.location = service.location
                    
                if service.date_event:
                    old_service.date_event = service.date_event
                
                if service.time_start:
                    old_service.time_start = service.time_start
                
                old_service.modifiedby = current_user.data.id
                old_service.modifiedon = datetime.utcnow()
                
                session.add(old_service)
                session.commit()
                session.refresh(old_service)
                
                response = Response(
                    success = True,
                    message = SuccessMessage.OperationSuccessful.value,
                    data = old_service
                )
            
            else:
                response.success = False
                response.message = ErrorMessage.NoEntry.value
                response.data = old_service
            
        return response
    
    async def delete_service(self, current_user: Annotated[SingleResponse[TokenData], Depends(get_current_active_user)],
                             id: int, 
                             session: Session = Depends(get_session)) -> Response[Service]:
        """delete a service

        Args:
            id (int): id of the service to delete
            session (Session, optional): dependency. Defaults to Depends(get_session).

        Returns:
            Response[Service]: return a reponse of the item deleted
        """  
        
        response: Response[Service]
        
        del_item: Optional[Service] = session.get(Service, id)
        
        if del_item:
            session.delete(del_item)
            session.commit()
            
            response = Response(
                success = True,
                message = SuccessMessage.OperationSuccessful.value,
                data = del_item
            )
            
        else:
            response.success = False
            response.message = ErrorMessage.NoEntry.value
            response.data = del_item
            
        return response
                   