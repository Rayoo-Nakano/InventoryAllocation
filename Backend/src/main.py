from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session
from schemas import TokenPayload, OrderRequest, InventoryRequest, AllocationRequest
from models import Order, Inventory, AllocationResult
from database import get_db
from allocation import allocate_inventory
from utils import COGNITO_JWKS_URL, COGNITO_AUDIENCE, COGNITO_ISSUER
import logging

app = FastAPI()

auth_scheme = HTTPBearer()

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

async def authenticate_user(auth_token: str = Depends(auth_scheme)):
    try:
        payload = jwt.decode(auth_token.credentials, COGNITO_JWKS_URL, audience=COGNITO_AUDIENCE, issuer=COGNITO_ISSUER)
        token_data = TokenPayload(**payload)
        return token_data
    except JWTError as e:
        logger.error(f"Invalid authentication token: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@app.post("/orders", dependencies=[Depends(authenticate_user)])
def create_order(order: OrderRequest, db: Session = Depends(get_db)):
    try:
        db_order = Order(item_code=order.item_code, quantity=order.quantity)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        logger.info(f"Order created: {db_order}")
        return db_order
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/orders", dependencies=[Depends(authenticate_user)])
def get_orders(db: Session = Depends(get_db)):
    try:
        orders = db.query(Order).all()
        logger.info(f"Retrieved {len(orders)} orders")
        return orders
    except Exception as e:
        logger.error(f"Error retrieving orders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/inventories", dependencies=[Depends(authenticate_user)])
def create_inventory(inventory: InventoryRequest, db: Session = Depends(get_db)):
    try:
        db_inventory = Inventory(item_code=inventory.item_code, quantity=inventory.quantity)
        db.add(db_inventory)
        db.commit()
        db.refresh(db_inventory)
        logger.info(f"Inventory created: {db_inventory}")
        return db_inventory
    except Exception as e:
        logger.error(f"Error creating inventory: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/inventories", dependencies=[Depends(authenticate_user)])
def get_inventories(db: Session = Depends(get_db)):
    try:
        inventories = db.query(Inventory).all()
        logger.info(f"Retrieved {len(inventories)} inventories")
        return inventories
    except Exception as e:
        logger.error(f"Error retrieving inventories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/allocate", dependencies=[Depends(authenticate_user)])
def allocate(allocation: AllocationRequest, db: Session = Depends(get_db)):
    try:
        allocation_result = allocate_inventory(allocation.order_id, allocation.item_code, allocation.quantity, db)
        logger.info(f"Allocation completed: {allocation_result}")
        return allocation_result
    except Exception as e:
        logger.error(f"Error allocating inventory: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/allocation-results", dependencies=[Depends(authenticate_user)])
def get_allocation_results(db: Session = Depends(get_db)):
    try:
        allocation_results = db.query(AllocationResult).all()
        logger.info(f"Retrieved {len(allocation_results)} allocation results")
        return allocation_results
    except Exception as e:
        logger.error(f"Error retrieving allocation results: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
