from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenDataExp(BaseModel):
    id: Optional[int]
    emailAddress: Optional[str]
    exp: int
    
class TokenData(BaseModel):
    id: Optional[int]
    emailAddress: Optional[str]