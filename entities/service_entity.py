from sqlmodel import SQLModel, Field, Column, Relationship, DateTime, Date
from typing import Optional, TYPE_CHECKING
from datetime import date, time, datetime
from pydantic import BaseModel
# from entities.user_entity import User

if TYPE_CHECKING:
    from entities.user_entity import User


class ServiceInput(SQLModel):
    servicetypeId: int = Field(foreign_key="servicetype.id")
    date_event: date = Field(sa_column=Column("date", Date))
    createdby: int = Field(foreign_key="user.id")
    time_start: time
    location: str

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "servicetypeId": 2,
                "date": 2024-5-12,
                "time_start": "2:00",
                "location": "Makarios Center"
            }
        }


class ServiceAndServiceTypeAndUserOutput(BaseModel):
    id: Optional[int]
    servicename: Optional[str]
    date_event: Optional[date] 
    createdby: Optional[str]
    modifiedby: Optional[str]
    time_start: Optional[time]
    location: Optional[str]
    modifiedon: Optional[datetime]
    createdon: Optional[datetime]
    

class ServiceOutput(ServiceInput):
    id: int


class Service(ServiceInput, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    createdon: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column("createdon", DateTime))
    modifiedon: Optional[datetime] = Field(
        default=None, sa_column=Column("modifiedon", DateTime))
    modifiedby: Optional[int] = Field(default=None)
    user: "User" = Relationship(back_populates="services")  # noqa: F821
