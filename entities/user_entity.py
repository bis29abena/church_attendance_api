# import necessary modules
from sqlmodel import SQLModel, Field, Column, VARCHAR, DateTime, Relationship
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from entities.members_entity import Member, MemberOutput
from entities.service_type_enity import ServiceType
from entities.service_entity import Service
from entities.attendance_type_entity import AttendanceType


class UserFilter(BaseModel):
    firstname: Optional[str] = None
    middlename: Optional[str] = None
    lastname: Optional[str] = None
    gender: Optional[str] = None
    emailaddress: Optional[str] = None
    disabled: Optional[bool] = None
    phoneNumber: Optional[str] = None

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "firstname": "Jane",
                "middlename": "Junior",
                "lastname": "foster",
                "gender": "male",
                "emailaddress": "jane@gmail.com",
                "phoneNumber": "0551890483",
                "password": "jhbcaublbjcsl5435",
                "disabled": True
            }
        }


class UserInput(SQLModel):
    firstname: str
    middlename: str
    lastname: str
    gender: str
    phoneNumber: str
    emailaddress: str = Field(sa_column=Column(
        "emailaddress", VARCHAR, unique=True, index=True))
    password: str
    disabled: bool = False

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "firstname": "Jane",
                "middlename": "Junior",
                "lastname": "foster",
                "gender": "male",
                "emailaddress": "jane@gmail.com",
                "phoneNumber": "0551890483",
                "password": "jhbcaublbjcsl5435",
                "disabled": False
            }
        }


class UserOutputMembers(SQLModel):
    id: int
    firstname: str
    middlename: str
    lastname: str
    gender: str
    phoneNumber: str
    emailaddress: str
    disabled: bool
    members: list[MemberOutput] = []


class UserOutput(SQLModel):
    id: int
    firstname: str
    middlename: str
    lastname: str
    gender: str
    phoneNumber: str
    emailaddress: str
    disabled: bool
    createdon: datetime
    modifiedon: Optional[datetime]
    


class User(UserInput, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    createdon: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column("createdon", DateTime))
    modifiedon: Optional[datetime] = Field(
        default=None, sa_column=Column("modifiedon", DateTime))
    members: list["Member"] = Relationship(back_populates="user")
    servicetypes: list["ServiceType"] = Relationship(back_populates="user")
    attendancetypes: list["AttendanceType"] = Relationship(
        back_populates="user")
    services: list["Service"] = Relationship(back_populates="user")
