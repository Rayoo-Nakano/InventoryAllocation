import logging
from sqlalchemy.orm import Session
from models import Order, Inventory, AllocationResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allocate_inventory(db: Session, strategy: str):
    logger.info(f"Starting inventory allocation with strategy: {strategy}")

    # 割り当て対象の注文を取得
    orders = db.query(Order).filter(Order.allocated == False).all()

    for order in orders:
        logger.info(f"Processing order {order.order_id} with item code {order.item_code} and quantity {order.quantity}")

        # 在庫を取得
        inventories = db.query(Inventory).filter(Inventory.item_code == order.item_code).order_by(Inventory.id).all()

        if strategy == "FIFO":
            remaining_quantity = order.quantity
            for inventory in inventories:
                if remaining_quantity <= 0:
                    break
                allocated_quantity = min(remaining_quantity, inventory.quantity)
                remaining_quantity -= allocated_quantity
                inventory.quantity -= allocated_quantity  # 在庫の数量を更新 (修正箇所: 行番号 27)
                logger.info(f"Allocated {allocated_quantity} units from inventory {inventory.id} at price {inventory.unit_price}")
                allocation_result = AllocationResult(
                    order_id=order.order_id,
                    allocated_quantity=allocated_quantity,
                    allocated_price=allocated_quantity * inventory.unit_price
                )
                db.add(allocation_result)

        elif strategy == "LIFO":
            remaining_quantity = order.quantity
            for inventory in reversed(inventories):
                if remaining_quantity <= 0:
                    break
                allocated_quantity = min(remaining_quantity, inventory.quantity)
                remaining_quantity -= allocated_quantity
                inventory.quantity -= allocated_quantity  # 在庫の数量を更新 (修正箇所: 行番号 44)
                logger.info(f"Allocated {allocated_quantity} units from inventory {inventory.id} at price {inventory.unit_price}")
                allocation_result = AllocationResult(
                    order_id=order.order_id,
                    allocated_quantity=allocated_quantity,
                    allocated_price=allocated_quantity * inventory.unit_price
                )
                db.add(allocation_result)

        elif strategy == "AVERAGE":
            total_quantity = sum(inventory.quantity for inventory in inventories)
            total_price = sum(inventory.quantity * inventory.unit_price for inventory in inventories)
            average_price = total_price / total_quantity if total_quantity > 0 else 0
            logger.info(f"Calculated average price: {average_price}")

            remaining_quantity = order.quantity
            total_allocated_price = 0
            for inventory in inventories:
                if remaining_quantity <= 0:
                    break
                allocated_quantity = min(remaining_quantity, inventory.quantity)
                remaining_quantity -= allocated_quantity
                inventory.quantity -= allocated_quantity
                logger.info(f"Allocated {allocated_quantity} units from inventory {inventory.id} at average price {average_price}")
                total_allocated_price += allocated_quantity * average_price
            
            # 1つの割当結果を作成 (修正箇所: 行番号 72-76)
            allocation_result = AllocationResult(
                order_id=order.order_id,
                allocated_quantity=order.quantity,
                allocated_price=total_allocated_price
            )
            db.add(allocation_result)

        elif strategy == "SPECIFIC":
            for inventory in inventories:
                if inventory.quantity >= order.quantity:
                    allocated_quantity = order.quantity
                    inventory.quantity -= allocated_quantity
                    logger.info(f"Allocated {allocated_quantity} units from specific inventory {inventory.id} at price {inventory.unit_price}")
                    allocation_result = AllocationResult(
                        order_id=order.order_id,
                        allocated_quantity=allocated_quantity,
                        allocated_price=allocated_quantity * inventory.unit_price  # 割り当てた在庫の価格を使用 (修正箇所: 行番号 92)
                    )
                    db.add(allocation_result)
                    break

        elif strategy == "TOTAL_AVERAGE":
            total_quantity = sum(inventory.quantity for inventory in inventories)
            total_price = sum(inventory.quantity * inventory.unit_price for inventory in inventories)
            total_average_price = total_price / total_quantity if total_quantity > 0 else 0
            logger.info(f"Calculated total average price: {total_average_price}")

            remaining_quantity = order.quantity
            for inventory in inventories:
                if remaining_quantity <= 0:
                    break
                allocated_quantity = min(remaining_quantity, inventory.quantity)
                remaining_quantity -= allocated_quantity
                inventory.quantity -= allocated_quantity
                logger.info(f"Allocated {allocated_quantity} units from inventory {inventory.id} at total average price {total_average_price}")
            
            total_allocated_price = order.quantity * total_average_price
            
            # 1つの割当結果を作成 (修正箇所: 行番号 114-118)
            allocation_result = AllocationResult(
                order_id=order.order_id,
                allocated_quantity=order.quantity,
                allocated_price=total_allocated_price
            )
            db.add(allocation_result)

        elif strategy == "MOVING_AVERAGE":
            window_size = 3
            prices = []
            remaining_quantity = order.quantity
            for inventory in inventories:
                if remaining_quantity <= 0:
                    break
                allocated_quantity = min(remaining_quantity, inventory.quantity)
                remaining_quantity -= allocated_quantity
                inventory.quantity -= allocated_quantity
                prices.append(inventory.unit_price)
                if len(prices) > window_size:
                    prices.pop(0)
                moving_average_price = sum(prices) / len(prices)  # 移動平均の計算を修正 (修正箇所: 行番号 136)
                logger.info(f"Allocated {allocated_quantity} units from inventory {inventory.id} at moving average price {moving_average_price}")
            
            total_allocated_price = order.quantity * moving_average_price
            
            # 1つの割当結果を作成 (修正箇所: 行番号 141-145)
            allocation_result = AllocationResult(
                order_id=order.order_id,
                allocated_quantity=order.quantity,
                allocated_price=total_allocated_price
            )
            db.add(allocation_result)

        else:
            raise ValueError(f"Unknown allocation strategy: {strategy}")

        logger.info(f"Created allocation result for order {order.order_id} with allocated quantity {order.quantity} and price {allocation_result.allocated_price}")
        order.allocated = True

    db.commit()
    logger.info("Inventory allocation completed")

def main():
    from database import SessionLocal
    db = SessionLocal()
    strategies = ["FIFO", "LIFO", "AVERAGE", "SPECIFIC", "TOTAL_AVERAGE", "MOVING_AVERAGE"]
    for strategy in strategies:
        allocate_inventory(db, strategy)

if __name__ == "__main__":
    main()
