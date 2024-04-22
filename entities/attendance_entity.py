from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from entities.members_entity import Member

class AttendanceInput(SQLModel):
    memberid: int = Field(foreign_key="member.id")
    serviceid: int = Field(foreign_key="service.id")
    attendancestatusid: int = Field(foreign_key="attendancetype.id")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "memberid": 2,
                "serviceid": 1,
                "attendancestatusid": 4
            }
        }


class AttendanceOutput(AttendanceInput):
    id: int


class Attendance(AttendanceInput, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    createdon: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column("createdon", DateTime))
    modifiedon: Optional[datetime] = Field(
        default=None, sa_column=Column("modifiedon", DateTime))
    member: "Member" = Relationship(back_populates="attendances")
