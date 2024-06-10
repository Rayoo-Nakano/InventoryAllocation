from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Order, Inventory, AllocationResult
from schemas import OrderRequest, InventoryRequest, AllocationRequest, OrderResponse, InventoryResponse, AllocationResultResponse, TokenPayload
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime
import logging

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ログ出力のフォーマットを設定
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# コンソールハンドラを作成し、フォーマットを設定
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# ロガーにコンソールハンドラを追加
logger.addHandler(console_handler)


app = FastAPI()

COGNITO_PUBLIC_KEYS = {
    "key_id_1": "public_key_1",
    "key_id_2": "public_key_2",
}

def authenticate_token(token: str) -> TokenPayload:
    """
    Amazon Cognitoが発行するJWTトークンを検証する関数
    """
    try:
        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="無効なトークンです")
        public_key = COGNITO_PUBLIC_KEYS.get(kid)
        if not public_key:
            raise HTTPException(status_code=401, detail="無効なトークンです")
        payload = jwt.decode(token, public_key, algorithms=["RS256"], audience="your_audience", issuer="your_issuer")
        return TokenPayload(**payload)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="無効なトークンです")
    
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
        payload = authenticate_token(token)
        request.state.user = payload
    except HTTPException as e:
        raise e
    response = await call_next(request)
    return response

@app.post("/orders", response_model=OrderResponse, status_code=201)  # ここにstatus_code=201を追加
def create_order(order: OrderRequest, db: Session = Depends(get_db), token_payload: TokenPayload = Depends(authenticate_token)):
    """
    注文を作成するエンドポイント
    """
    db_order = Order(item_code=order.item_code, quantity=order.quantity)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # レスポンスデータをログ出力
    logger.debug(f"Response data: {db_order.__dict__}")
    
    return db_order

@app.get("/orders", response_model=list[OrderResponse])
def read_orders(db: Session = Depends(get_db), token_payload: TokenPayload = Depends(authenticate_token)):
    """
    注文一覧を取得するエンドポイント
    """
    orders = db.query(Order).all()
    return orders

@app.post("/inventories", response_model=InventoryResponse, status_code=201)  # ここにstatus_code=201を追加
def create_inventory(inventory: InventoryRequest, db: Session = Depends(get_db), token_payload: TokenPayload = Depends(authenticate_token)):
    """
    在庫を作成するエンドポイント
    """
    receipt_date = datetime.strptime(inventory.receipt_date, "%Y-%m-%d").date()
    db_inventory = Inventory(item_code=inventory.item_code, quantity=inventory.quantity, receipt_date=receipt_date, unit_price=inventory.unit_price)
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

@app.get("/inventories", response_model=list[InventoryResponse])
def read_inventories(db: Session = Depends(get_db), token_payload: TokenPayload = Depends(authenticate_token)):
    """
    在庫一覧を取得するエンドポイント
    """
    inventories = db.query(Inventory).all()
    return inventories

@app.post("/orders/{order_id}/allocate", response_model=AllocationResultResponse)
def allocate_inventory(order_id: int, allocation: AllocationRequest, db: Session = Depends(get_db), token_payload: TokenPayload = Depends(authenticate_token)):
    """
    在庫を割り当てるエンドポイント
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    inventory = db.query(Inventory).filter(Inventory.item_code == allocation.item_code, Inventory.quantity >= allocation.quantity).order_by(Inventory.receipt_date).first()

    if not order:
        raise HTTPException(status_code=404, detail="注文が見つかりません")
    if not inventory:
        raise HTTPException(status_code=404, detail="十分な在庫がありません")

    inventory.quantity -= allocation.quantity
    allocation_date = datetime.strptime(allocation.allocation_date, "%Y-%m-%d").date()
    db_allocation = AllocationResult(order_id=order.id, item_code=inventory.item_code, allocated_quantity=allocation.quantity, allocated_price=inventory.unit_price, allocation_date=allocation_date)
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    return db_allocation

@app.get("/allocation-results", response_model=list[AllocationResultResponse])
def read_allocation_results(db: Session = Depends(get_db), token_payload: TokenPayload = Depends(authenticate_token)):
    """
    割り当て結果一覧を取得するエンドポイント
    """
    allocation_results = db.query(AllocationResult).all()
    return allocation_results
