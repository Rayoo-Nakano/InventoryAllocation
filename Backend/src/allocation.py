from sqlalchemy.orm import Session
from models import Order, Inventory, AllocationResult
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def allocate_inventory(db: Session, allocation_method: str):
    orders = db.query(Order).all()
    inventories = db.query(Inventory).all()
    
    allocation_results = []
    
    for order in orders:
        allocated_quantity = 0
        allocated_price = 0
        
        try:
            if allocation_method == "FIFO":
                for inventory in inventories:
                    if inventory.item_code == order.item_code and inventory.quantity > 0:
                        if inventory.quantity >= order.quantity - allocated_quantity:
                            allocated_quantity += order.quantity - allocated_quantity
                            allocated_price += (order.quantity - allocated_quantity) * inventory.unit_price
                            inventory.quantity -= order.quantity - allocated_quantity
                        else:
                            allocated_quantity += inventory.quantity
                            allocated_price += inventory.quantity * inventory.unit_price
                            inventory.quantity = 0
                        
                        if allocated_quantity == order.quantity:
                            break
            
            elif allocation_method == "LIFO":
                for inventory in reversed(inventories):
                    if inventory.item_code == order.item_code and inventory.quantity > 0:
                        if inventory.quantity >= order.quantity - allocated_quantity:
                            allocated_quantity += order.quantity - allocated_quantity
                            allocated_price += (order.quantity - allocated_quantity) * inventory.unit_price
                            inventory.quantity -= order.quantity - allocated_quantity
                        else:
                            allocated_quantity += inventory.quantity
                            allocated_price += inventory.quantity * inventory.unit_price
                            inventory.quantity = 0
                        
                        if allocated_quantity == order.quantity:
                            break
            
            elif allocation_method == "AVERAGE":
                total_quantity = sum(inventory.quantity for inventory in inventories if inventory.item_code == order.item_code)
                total_price = sum(inventory.quantity * inventory.unit_price for inventory in inventories if inventory.item_code == order.item_code)
                
                if total_quantity >= order.quantity:
                    average_price = total_price / total_quantity
                    allocated_quantity = order.quantity
                    allocated_price = order.quantity * average_price
                    
                    for inventory in inventories:
                        if inventory.item_code == order.item_code:
                            if inventory.quantity >= order.quantity:
                                inventory.quantity -= order.quantity
                                order.quantity = 0
                            else:
                                order.quantity -= inventory.quantity
                                inventory.quantity = 0
                            
                            if order.quantity == 0:
                                break
            
            elif allocation_method == "SPECIFIC":
                for inventory in inventories:
                    if inventory.item_code == order.item_code and inventory.quantity >= order.quantity:
                        allocated_quantity = order.quantity
                        allocated_price = order.quantity * inventory.unit_price
                        inventory.quantity -= order.quantity
                        break
            
            elif allocation_method == "TOTAL_AVERAGE":
                total_quantity = sum(inventory.quantity for inventory in inventories)
                total_price = sum(inventory.quantity * inventory.unit_price for inventory in inventories)
                
                if total_quantity >= order.quantity:
                    average_price = total_price / total_quantity
                    allocated_quantity = order.quantity
                    allocated_price = order.quantity * average_price
                    
                    for inventory in inventories:
                        if inventory.quantity >= order.quantity:
                            inventory.quantity -= order.quantity
                            order.quantity = 0
                        else:
                            order.quantity -= inventory.quantity
                            inventory.quantity = 0
                        
                        if order.quantity == 0:
                            break
            
            elif allocation_method == "MOVING_AVERAGE":
                total_quantity = 0
                total_price = 0
                
                for inventory in inventories:
                    if inventory.item_code == order.item_code:
                        total_quantity += inventory.quantity
                        total_price += inventory.quantity * inventory.unit_price
                        
                        if total_quantity >= order.quantity:
                            average_price = total_price / total_quantity
                            allocated_quantity = order.quantity
                            allocated_price = order.quantity * average_price
                            
                            inventory.quantity -= order.quantity
                            break
            
            else:
                raise ValueError("Invalid allocation method")
            
            allocation_result = AllocationResult(
                order_id=order.order_id,
                item_code=order.item_code,
                allocated_quantity=allocated_quantity,
                allocated_price=allocated_price,
                allocation_date=datetime.now().date()
            )
            
            allocation_results.append(allocation_result)
            
            logger.info(f"Allocation completed for order {order.order_id}. Allocated quantity: {allocated_quantity}, Allocated price: {allocated_price}")
        
        except Exception as e:
            logger.error(f"Error during allocation for order {order.order_id}: {str(e)}")
            raise
    
    db.bulk_save_objects(allocation_results)
    db.commit()
    
    return allocation_results