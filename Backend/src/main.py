from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Order, Inventory, AllocationResult, Item
from database import SessionLocal, engine
from schemas import OrderRequest, InventoryRequest, AllocationRequest
from allocation import allocate_inventory
import logging

app = FastAPI()

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/orders")
def create_order(order: OrderRequest, db: Session = Depends(get_db)):
    try:
        db_order = Order(order_id=order.order_id, item_code=order.item_code, quantity=order.quantity)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        logger.info(f"Order created: {db_order}")
        return db_order
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    try:
        orders = db.query(Order).all()
        logger.info(f"Retrieved {len(orders)} orders")
        return orders
    except Exception as e:
        logger.error(f"Error retrieving orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/inventories")
def create_inventory(inventory: InventoryRequest, db: Session = Depends(get_db)):
    try:
        db_inventory = Inventory(item_code=inventory.item_code, quantity=inventory.quantity,
                                 receipt_date=inventory.receipt_date, unit_price=inventory.unit_price)
        db.add(db_inventory)
        db.commit()
        db.refresh(db_inventory)
        logger.info(f"Inventory created: {db_inventory}")
        return db_inventory
    except Exception as e:
        logger.error(f"Error creating inventory: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/inventories")
def get_inventories(db: Session = Depends(get_db)):
    try:
        inventories = db.query(Inventory).all()
        logger.info(f"Retrieved {len(inventories)} inventories")
        return inventories
    except Exception as e:
        logger.error(f"Error retrieving inventories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/allocate")
def allocate(allocation: AllocationRequest, db: Session = Depends(get_db)):
    try:
        result = allocate_inventory(db, allocation.allocation_method)
        logger.info(f"Allocation completed. Results: {result}")
        return result
    except ValueError as e:
        logger.error(f"Invalid allocation method: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid allocation method")
    except Exception as e:
        logger.error(f"Error during allocation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/allocation-results")
def get_allocation_results(db: Session = Depends(get_db)):
    try:
        allocation_results = db.query(AllocationResult).all()
        logger.info(f"Retrieved {len(allocation_results)} allocation results")
        return allocation_results
    except Exception as e:
        logger.error(f"Error retrieving allocation results: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

def lambda_handler(event, context):
    return app(event, context)