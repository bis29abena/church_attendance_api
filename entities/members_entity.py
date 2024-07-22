from sqlmodel import Field, Column, VARCHAR, DateTime, SQLModel, Date, LargeBinary, Relationship, CheckConstraint
from typing import Optional, TYPE_CHECKING, AnyStr
from datetime import date, datetime
from entities.attendance_entity import Attendance
from pydantic import BaseModel, EmailStr, field_validator
from re import Pattern
from PIL import Image
from io import BytesIO

import re

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
    profile_picture: Optional[bytes] = None
    file_size: int = Field(..., gt=0)
    house_address: str
    title_id: int
    createdby: int 
    
    @field_validator("phonenumber")
    def validate_phone_number(cls, value: str) -> str:
        phone_regex: Pattern[AnyStr] = re.compile(r'^(0\d{9}|\+233\d{9})$')
        
        if not phone_regex.match(value):
            raise ValueError("This is not a valid Ghanaian phone number")
        
        return value
    
    @field_validator("profile_picture")
    def validate_profile_picture(cls,values: dict, value: bytes | None = None) -> bytes | None:
        if not value:
            return value
        
        try:
            image = Image.open(BytesIO(value))
            
            image.verify() # check if is an image
        except(IOError, SyntaxError, TypeError) as e:
            raise ValueError("File provided is not an image") from e
        
        
         # Calculate the file size
        file_size: int = len(value)
        values['file_size'] = file_size  # Assign the file size

        # Check the file size if it's in a desired limit (example: less than 5MB)
        max_file_size = 5 * 1024 * 1024  # 5MB in bytes
        if file_size > max_file_size:
            raise ValueError(f'File size exceeds the limit of {max_file_size} bytes')

        return value
        
        
    
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
