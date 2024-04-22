from fastapi import APIRouter, Depends
from entities.title_entity import Title, TitleInput, TitleOutput
from db import get_session
from sqlmodel import Session, select, column
from dto.response import Response
from typing import Optional, Sequence, List
from enums.enums import SuccessMessage, ErrorMessage
from datetime import datetime


class TitleRouter(APIRouter):
    def __init__(self):
        super().__init__(prefix="/api/titles")
        self.setup_routes()

    def setup_routes(self):
        self.add_api_route(path="/getAll", endpoint=self.get_titles,
                           methods=["GET"], response_model=Response[TitleOutput])
        self.add_api_route(path="/getbyId/{title_id}", endpoint=self.get_title_id,
                           methods=["GET"], response_model=Response[Title])
        self.add_api_route(path="/addtitle", endpoint=self.add_title,
                           methods=["POST"], response_model=Response[Title])
        self.add_api_route(path="/updatetitle/{id}", methods=[
                           "PUT"], endpoint=self.change_title, response_model=Response[TitleOutput])
        self.add_api_route(path="/deletetitle/{id}", methods=[
                           "DELETE"], endpoint=self.remove_title, response_model=Response[TitleOutput])

    async def get_titles(self, name: Optional[str] = None, session: Session = Depends(get_session)) -> Response[Title]:
        """Get All titles in the church

        Args:
            name (Optional[str], optional): if name is specified. Defaults to None.
            session (Session, optional): dependency. Defaults to Depends(get_session).

        Returns:
            Reponse[Title]: Return a response of the Title Model
        """
        query = select(Title)
        response: Response[Title]

        if name:
            query = query.where(column("title_name").like(f"%{name}%"))
            
        results: Sequence[Title] = session.exec(query).all()

        if results:
            result: List[Title] = list(results)
            
            response = Response(
                success=True,
                message=SuccessMessage.OperationSuccessful.value,
                data=result
            )
        else:
            return Response(success=False, message=ErrorMessage.NoTitleFound.value, data=None)

        return response

    async def get_title_id(self, title_id: int, session: Session = Depends(get_session)) -> Response[Title]:
        """get title by ID

        Args:
            title_id (int): Title ID
            session (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[TitleOutput]: Return a reponse of Title
        """
        title = session.get(Title, title_id)

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
                message=ErrorMessage.TitleNotFound.value,
                data=title
            )
        return response

    async def add_title(self, car: TitleInput, session: Session = Depends(get_session)) -> Response[Title]:
        """Add new title to the table

        Args:
            car (TitleInput): car data to be added
            session (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[Title]: Return a reponse of the Title Created
        """
        response = None

        new_title = Title.from_orm(car)
        session.add(new_title)
        session.commit()
        session.refresh(new_title)
        if new_title:
            response = Response(
                success=True,
                message=SuccessMessage.TitleAdded.value,
                data=new_title,
            )
        else:
            return Response(success=True, message=ErrorMessage.TitleNotAdded.value, data=None)

        return response

    async def change_title(self, id: int, new_title: TitleInput, session: Session = Depends(get_session)) -> Response[Title]:
        """Update title

        Args:
            id (int): Id of the old Title
            new_title (TitleInput): Data for the new title
            session (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[TitleOutput]: Return a response of Title OutPut
        """
        response: Response[Title]
        old_title = session.get(Title, id)

        if old_title:
            old_title.title_name = new_title.title_name
            old_title.modifiedon = datetime.utcnow()
            session.commit()
            session.refresh(old_title)

            response = Response(
                success=True,
                message=SuccessMessage.OperationSuccessful.value,
                data=old_title
            )
        else:

            response = Response(
                success=False,
                message=ErrorMessage.TileNotUpdate.value,
                data=old_title
            )
        return response

    async def remove_title(self, id: int, session: Session = Depends(get_session)) -> Response[Title]:
        """Remove a title

        Args:
            id (int): Id of the item to remove
            session (Session, optional): Dependency. Defaults to Depends(get_session).

        Returns:
            Response[TitleOutput]: Reponse Object of the title to remove
        """
        response = None

        title_del = session.get(Title, id)

        if title_del:
            session.delete(title_del)
            session.commit()

            response = Response(
                success=True,
                message=SuccessMessage.TitleRemoved.value,
                data=title_del
            )

        else:
            response = Response(
                success=True,
                message=ErrorMessage.TitleNotFound.value,
                data=title_del
            )
        return response
