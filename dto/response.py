from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | list[T] | None
    
class SingleResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None