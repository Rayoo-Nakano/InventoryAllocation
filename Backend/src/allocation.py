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

def allocate_inventory(db: Session, allocation_strategy: str):
    logger.info(f"Starting inventory allocation with strategy: {allocation_strategy}")

    # 割り当て対象の注文を取得
    orders = db.query(Order).filter(Order.quantity > 0).all()

    for order in orders:
        remaining_quantity = order.quantity
        allocated_quantity = 0
        allocated_price = 0.0

        logger.info(f"Processing order {order.order_id} with item code {order.item_code} and quantity {order.quantity}")

        if allocation_strategy == "FIFO":
            # 在庫を取得し、入荷日時の昇順でソート
            inventories = db.query(Inventory).filter(Inventory.item_code == order.item_code, Inventory.quantity > 0).order_by(Inventory.id).all()

            for inventory in inventories:
                if remaining_quantity <= 0:
                    break

                # 割り当てる数量を計算
                quantity_to_allocate = min(remaining_quantity, inventory.quantity)
                allocated_quantity += quantity_to_allocate
                allocated_price += quantity_to_allocate * inventory.unit_price
                remaining_quantity -= quantity_to_allocate
                inventory.quantity -= quantity_to_allocate

                logger.info(f"Allocated {quantity_to_allocate} units from inventory {inventory.id} at price {inventory.unit_price}")

        elif allocation_strategy == "LIFO":
            # 在庫を取得し、入荷日時の降順でソート
            inventories = db.query(Inventory).filter(Inventory.item_code == order.item_code, Inventory.quantity > 0).order_by(Inventory.created_at.desc()).all()

            for inventory in inventories:
                if remaining_quantity <= 0:
                    break

                # 割り当てる数量を計算
                quantity_to_allocate = min(remaining_quantity, inventory.quantity)
                allocated_quantity += quantity_to_allocate
                allocated_price += quantity_to_allocate * inventory.unit_price
                remaining_quantity -= quantity_to_allocate
                inventory.quantity -= quantity_to_allocate

                logger.info(f"Allocated {quantity_to_allocate} units from inventory {inventory.id} at price {inventory.unit_price}")

        elif allocation_strategy == "AVERAGE":
            # 在庫を取得し、単価の昇順でソート
            inventories = db.query(Inventory).filter(Inventory.item_code == order.item_code, Inventory.quantity > 0).order_by(Inventory.unit_price).all()

            # 在庫の総数量と総価格を計算
            total_quantity = sum(inventory.quantity for inventory in inventories)
            total_price = sum(inventory.quantity * inventory.unit_price for inventory in inventories)

            # 在庫の平均単価を計算
            average_price = total_price / total_quantity if total_quantity > 0 else 0.0

            logger.info(f"Calculated average price: {average_price}")

            for inventory in inventories:
                if remaining_quantity <= 0:
                    break

                # 割り当てる数量を計算
                quantity_to_allocate = min(remaining_quantity, inventory.quantity)
                allocated_quantity += quantity_to_allocate
                allocated_price += quantity_to_allocate * average_price
                remaining_quantity -= quantity_to_allocate
                inventory.quantity -= quantity_to_allocate

                logger.info(f"Allocated {quantity_to_allocate} units from inventory {inventory.id} at average price {average_price}")

        elif allocation_strategy == "SPECIFIC":
            # 在庫を取得し、特定の在庫IDを指定して割り当てる
            inventory_id = 1  # 割り当てる在庫IDを指定
            inventory = db.query(Inventory).filter(Inventory.id == inventory_id, Inventory.item_code == order.item_code, Inventory.quantity > 0).first()

            if inventory:
                # 割り当てる数量を計算
                quantity_to_allocate = min(remaining_quantity, inventory.quantity)
                allocated_quantity += quantity_to_allocate
                allocated_price += quantity_to_allocate * inventory.unit_price
                remaining_quantity -= quantity_to_allocate
                inventory.quantity -= quantity_to_allocate

                logger.info(f"Allocated {quantity_to_allocate} units from specific inventory {inventory.id} at price {inventory.unit_price}")
            else:
                logger.warning(f"Specific inventory {inventory_id} not found or out of stock for order {order.order_id}")

        elif allocation_strategy == "TOTAL_AVERAGE":
            # 在庫を取得し、総平均単価を計算
            inventories = db.query(Inventory).filter(Inventory.item_code == order.item_code, Inventory.quantity > 0).all()

            # 在庫の総数量と総価格を計算
            total_quantity = sum(inventory.quantity for inventory in inventories)
            total_price = sum(inventory.quantity * inventory.unit_price for inventory in inventories)

            # 在庫の総平均単価を計算
            total_average_price = total_price / total_quantity if total_quantity > 0 else 0.0

            logger.info(f"Calculated total average price: {total_average_price}")

            for inventory in inventories:
                if remaining_quantity <= 0:
                    break

                # 割り当てる数量を計算
                quantity_to_allocate = min(remaining_quantity, inventory.quantity)
                allocated_quantity += quantity_to_allocate
                allocated_price += quantity_to_allocate * total_average_price
                remaining_quantity -= quantity_to_allocate
                inventory.quantity -= quantity_to_allocate

                logger.info(f"Allocated {quantity_to_allocate} units from inventory {inventory.id} at total average price {total_average_price}")

        elif allocation_strategy == "MOVING_AVERAGE":
            # 在庫を取得し、移動平均単価を計算
            inventories = db.query(Inventory).filter(Inventory.item_code == order.item_code, Inventory.quantity > 0).order_by(Inventory.created_at).all()

            # 移動平均単価を計算するための変数を初期化
            moving_total_quantity = 0
            moving_total_price = 0.0
            moving_average_price = 0.0

            for inventory in inventories:
                if remaining_quantity <= 0:
                    break

                # 移動平均単価を計算
                moving_total_quantity += inventory.quantity
                moving_total_price += inventory.quantity * inventory.unit_price
                moving_average_price = moving_total_price / moving_total_quantity

                # 割り当てる数量を計算
                quantity_to_allocate = min(remaining_quantity, inventory.quantity)
                allocated_quantity += quantity_to_allocate
                allocated_price += quantity_to_allocate * moving_average_price
                remaining_quantity -= quantity_to_allocate
                inventory.quantity -= quantity_to_allocate

                logger.info(f"Allocated {quantity_to_allocate} units from inventory {inventory.id} at moving average price {moving_average_price}")

        else:
            logger.error(f"Invalid allocation strategy: {allocation_strategy}")
            raise ValueError("Invalid allocation strategy")

        if allocated_quantity > 0:
            # 割り当て結果を作成
            allocation_result = AllocationResult(
                order_id=order.order_id,
                allocated_quantity=allocated_quantity,
                allocated_price=allocated_price
            )
            db.add(allocation_result)
            order.quantity -= allocated_quantity  # 注文の数量を更新

            logger.info(f"Created allocation result for order {order.order_id} with allocated quantity {allocated_quantity} and price {allocated_price}")
        else:
            logger.warning(f"No inventory allocated for order {order.order_id}")

    # 変更をコミット
    db.commit()

    logger.info("Inventory allocation completed")
