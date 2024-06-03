from pydantic import BaseModel
from datetime import date

class OrderRequest(BaseModel):
    order_id: str
    item_code: str
    quantity: int

class InventoryRequest(BaseModel):
    item_code: str
    quantity: int
    receipt_date: date
    unit_price: float

class AllocationRequest(BaseModel):
    allocation_method: str

class OrderResponse(BaseModel):
    order_id: str
    item_code: str
    quantity: int

    class Config:
        orm_mode = True

class InventoryResponse(BaseModel):
    item_code: str
    quantity: int
    receipt_date: date
    unit_price: float

    class Config:
        orm_mode = True

class AllocationResultResponse(BaseModel):
    allocation_id: int
    order_id: str
    item_code: str
    allocated_quantity: int
    allocated_price: float
    allocation_date: date

    class Config:
        orm_mode = True
