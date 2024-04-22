from sqlmodel import SQLModel, Field, Column, DateTime, VARCHAR
from typing import Optional
from datetime import datetime


class TitleInput(SQLModel):
    title_name: str = Field(sa_column=Column(unique=True, index=True, type_=VARCHAR))

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "title": "Pastor"
            }
        }


class TitleOutput(TitleInput):
    id: int


class Title(TitleInput, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    createdon: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column("createdon", DateTime))
    modifiedon: Optional[datetime] = Field(
        default=None, sa_column=Column("modifiedon", DateTime))
