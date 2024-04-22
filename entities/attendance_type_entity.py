from sqlmodel import SQLModel, Field, Column, VARCHAR, DateTime, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel

if TYPE_CHECKING:
    from entities.user_entity import User


class AttendanceTypeInput(SQLModel):
    name: str = Field(sa_column=Column("name", VARCHAR, index=True))
    createdby: int = Field(foreign_key="user.id")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "name": "Present"
            }
        }


class AttendanceTypeOutput(AttendanceTypeInput):
    id: int


class AttendanceTypeUser(BaseModel):
    id: Optional[int]
    name: str
    email_createdby: str
    email_modifiedby: Optional[str | int] = None
    createdon: datetime
    modifiedon: Optional[datetime] = None


class AttendanceType(AttendanceTypeInput, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    createdon: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column("createdon", DateTime))
    modifiedon: Optional[datetime] = Field(
        default=None, sa_column=Column("modifiedon", DateTime))

    modifiedby: Optional[int] = Field(default=None)
    user: "User" = Relationship(back_populates="attendancetypes")  
