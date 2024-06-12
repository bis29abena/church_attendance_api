from sqlmodel import Field, Column, VARCHAR, DateTime, SQLModel, Date, LargeBinary, Relationship, CheckConstraint
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime
from entities.attendance_entity import Attendance
from pydantic import BaseModel, EmailStr

if TYPE_CHECKING:
    from entities.user_entity import User
    from entities.attendance_entity import Attendance


class MemberInput(SQLModel):
    firstname: str
    lastname: str
    middlename: str
    gender: str
    emailaddress: str = Field(sa_column=Column(
        "emailaddress", VARCHAR, unique=True, index=True))
    phonenumber: str
    dob: date = Field(sa_column=Column("dob", Date))
    profile_picture: Optional[bytes] = Field(
        default=None, sa_column=Column("profile_picture", LargeBinary))
    house_address: str
    title_id: int = Field(foreign_key="title.id")

    class ConfigDict:
        json_schema_extra = {
            "exmaple": {
                "firstname": "Jane",
                "lastname": "Foster",
                "middlename": "Junior",
                "gender": "male",
                "emailaddress": "jane@gamil.com",
                "phonenumber": "0244154585",
                "dob": 2024/5/12,
                "house_address": "GPS-Address",
                "title_id": 2
            }
        }


class MemberInputData(BaseModel):
    firstname: str
    lastname: str
    middlename: str
    gender: str
    emailaddress: EmailStr
    phonenumber: str
    dob: date
    profile_picture: bytes
    house_address: str
    title_id: int
    createdby: int 
    
class MemberOutput(MemberInput):
    id: int


class Member(MemberInput, table=True, ):
    id: Optional[int] = Field(default=None, primary_key=True)
    createdby: int = Field(foreign_key="user.id")
    modifiedby: Optional[int] = Field(default=None)
    createdon: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column("createdon", DateTime))
    modifiedon: Optional[datetime] = Field(
        default=None, sa_column=Column("modifiedon", DateTime))
    user: "User" = Relationship(back_populates="members")  
    attendances: list["Attendance"] = Relationship(back_populates="member")  
    

    # Adding a constraint to limit the size of the image_data column
    __table_args__ = (
        CheckConstraint('LENGTH(profile_picture) <= :profile_picture_size',
                        name='profile_picture_length_check'),
    )

    # You may specify the maximum image size in bytes
    profile_picture_size: int = 5 * 1024 * 1024  # 5 MB
