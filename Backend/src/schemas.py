from pydantic import BaseModel
from datetime import datetime, date
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
    item_code: str  # 商品コード
    quantity: int  # 数量

class InventoryRequest(BaseModel):
    item_code: str  # 商品コード
    quantity: int  # 数量
    receipt_date: date  # 入荷日
    unit_price: float  # 単価

class AllocationRequest(BaseModel):
    order_id: int  # 注文ID
    item_code: str  # 商品コード
    quantity: int  # 数量
    allocation_date: date  # 割当日

class OrderResponse(BaseModel):
    order_id: int  # 注文ID
    item_code: str  # 商品コード
    quantity: int  # 数量
    allocated: bool  # 割当済みかどうかを示すフラグ

    class Config:
        orm_mode = True

class InventoryResponse(BaseModel):
    id: int  # 在庫ID
    item_code: str  # 商品コード
    quantity: int  # 数量
    receipt_date: date  # 入荷日
    unit_price: float  # 単価
    created_at: datetime  # 作成日時

    class Config:
        orm_mode = True

class AllocationResultResponse(BaseModel):
    id: int  # 割当結果ID
    order_id: int  # 注文ID
    item_code: str  # 商品コード
    allocated_quantity: int  # 割当数量
    allocated_price: float  # 割当価格
    allocation_date: date  # 割当日

    class Config:
        orm_mode = True
