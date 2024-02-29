from pydantic import BaseModel, Field
from typing import Optional

class Account(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    wallet: Optional[str] = None


class RegisterRequest(BaseModel):
    first_name: str = Field(..., serialization_alias='firstName')
    last_name: str = Field(..., serialization_alias='lastName')
    email: str
    wallet: str
    address1: str = Field(..., serialization_alias='address') 
    city: str
    state: str
    postal_code: str = Field(..., serialization_alias='postalCode')

    class Config:
        populate_by_name = True
