from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Order, Inventory, AllocationResult
from schemas import OrderRequest, InventoryRequest, AllocationRequest, OrderResponse, InventoryResponse, AllocationResultResponse

app = FastAPI()

@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderRequest, db: Session = Depends(get_db)):
    """
    注文を作成するエンドポイント
    """
    db_order = Order(item_code=order.item_code, quantity=order.quantity)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return OrderResponse.from_orm(db_order)

@app.get("/orders", response_model=list[OrderResponse])
def read_orders(db: Session = Depends(get_db)):
    """
    注文一覧を取得するエンドポイント
    """
    orders = db.query(Order).all()
    return [OrderResponse.from_orm(order) for order in orders]

@app.post("/inventories", response_model=InventoryResponse)
def create_inventory(inventory: InventoryRequest, db: Session = Depends(get_db)):
    """
    在庫を作成するエンドポイント
    """
    db_inventory = Inventory(item_code=inventory.item_code, quantity=inventory.quantity, receipt_date=inventory.receipt_date, unit_price=inventory.unit_price)
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return InventoryResponse.from_orm(db_inventory)

@app.get("/inventories", response_model=list[InventoryResponse])
def read_inventories(db: Session = Depends(get_db)):
    """
    在庫一覧を取得するエンドポイント
    """
    inventories = db.query(Inventory).all()
    return [InventoryResponse.from_orm(inventory) for inventory in inventories]

@app.post("/allocate", response_model=AllocationResultResponse)
def allocate_inventory(allocation: AllocationRequest, db: Session = Depends(get_db)):
    """
    在庫を割り当てるエンドポイント
    """
    order = db.query(Order).filter(Order.order_id == allocation.order_id).first()
    inventory = db.query(Inventory).filter(Inventory.item_code == allocation.item_code).first()

    if not order:
        raise HTTPException(status_code=404, detail="注文が見つかりません")
    if not inventory:
        raise HTTPException(status_code=404, detail="在庫が見つかりません")
    if inventory.quantity < allocation.quantity:
        raise HTTPException(status_code=400, detail="在庫数が不足しています")

    inventory.quantity -= allocation.quantity
    db_allocation = AllocationResult(order_id=order.order_id, item_code=inventory.item_code, allocated_quantity=allocation.quantity, allocated_price=inventory.unit_price, allocation_date=allocation.allocation_date)
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    return AllocationResultResponse.from_orm(db_allocation)

@app.get("/allocation-results", response_model=list[AllocationResultResponse])
def read_allocation_results(db: Session = Depends(get_db)):
    """
    割り当て結果一覧を取得するエンドポイント
    """
    allocation_results = db.query(AllocationResult).all()
    return [AllocationResultResponse.from_orm(result) for result in allocation_results]

def authenticate_token(token: str):
    """
    認証トークンを検証する関数
    """
    if token != "valid_token":
        raise HTTPException(status_code=401, detail="無効な認証トークンです")

@app.middleware("http")
async def authentication_middleware(request, call_next):
    """
    認証ミドルウェア
    """
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="認証トークンが見つからないか、無効です")
    token = token.split(" ")[1]
    try:
        authenticate_token(token)
    except HTTPException as e:
        raise e
    response = await call_next(request)
    return response
