from pydantic import BaseModel
from datetime import datetime
from typing import List

class TokenPayload(BaseModel):
    sub: str
    cognito_username: str
    email: str
    email_verified: bool
    given_name: str
    family_name: str
    roles: List[str]
    iss: str
    aud: str
    exp: int
    iat: int

class OrderRequest(BaseModel):
    item_code: str
    quantity: int

class InventoryRequest(BaseModel):
    item_code: str
    quantity: int

class AllocationRequest(BaseModel):
    order_id: int
    item_code: str
    quantity: int

class OrderResponse(BaseModel):
    id: int
    item_code: str
    quantity: int

    class Config:
        orm_mode = True

class InventoryResponse(BaseModel):
    id: int
    item_code: str
    quantity: int

    class Config:
        orm_mode = True

class AllocationResultResponse(BaseModel):
    id: int
    order_id: int
    item_code: str
    allocated_quantity: int
    allocation_date: datetime

    class Config:
        orm_mode = True
