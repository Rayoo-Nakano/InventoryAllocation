import logging
from sqlalchemy.orm import Session
from models import Order, Inventory, AllocationResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allocate_inventory(db: Session, strategy: str):
    """
    在庫割り当てを実行する関数
    :param db: データベースセッション
    :param strategy: 割り当て戦略
    """
    logger.info(f"Starting inventory allocation with strategy: {strategy}")

    # 割り当て対象の注文を取得
    orders = db.query(Order).filter(Order.allocated == False).all()

    for order in orders:
        logger.info(f"Processing order {order.id} with item code {order.item_code} and quantity {order.quantity}")

        # 在庫を取得
        inventories = db.query(Inventory).filter(Inventory.item_code == order.item_code).order_by(Inventory.id).all()

        # 割り当て戦略に応じて在庫割り当てを実行
        if strategy == "FIFO":
            allocate_fifo(db, order, inventories)
        elif strategy == "LIFO":
            allocate_lifo(db, order, inventories)
        elif strategy == "AVERAGE":
            allocate_average(db, order, inventories)
        elif strategy == "SPECIFIC":
            allocate_specific(db, order, inventories)
        elif strategy == "TOTAL_AVERAGE":
            allocate_total_average(db, order, inventories)
        elif strategy == "MOVING_AVERAGE":
            allocate_moving_average(db, order, inventories)
        else:
            raise ValueError(f"Unknown allocation strategy: {strategy}")

        logger.info(f"Allocation completed for order {order.id}")
        order.allocated = True

    db.commit()
    logger.info("Inventory allocation completed")

def allocate_fifo(db: Session, order: Order, inventories: list[Inventory]):
    """
    FIFO戦略で在庫割り当てを実行する関数
    :param db: データベースセッション
    :param order: 割り当て対象の注文
    :param inventories: 在庫リスト

    FIFO (First-In-First-Out) 引当:
    - 説明: 先入先出法。最も古い在庫から順番に引き当てる方法。
    - 数式: 
      - 引当数量 = min(注文数量, 在庫数量)
      - 引当価格 = 引当数量 × 在庫単価
    """
    remaining_quantity = order.quantity
    for inventory in inventories:
        if remaining_quantity <= 0:
            break
        allocated_quantity = min(remaining_quantity, inventory.quantity)
        remaining_quantity -= allocated_quantity
        inventory.quantity -= allocated_quantity
        create_allocation_result(db, order, allocated_quantity, allocated_quantity * inventory.unit_price)

def allocate_lifo(db: Session, order: Order, inventories: list[Inventory]):
    """
    LIFO戦略で在庫割り当てを実行する関数
    :param db: データベースセッション
    :param order: 割り当て対象の注文
    :param inventories: 在庫リスト

    LIFO (Last-In-First-Out) 引当:
    - 説明: 後入先出法。最も新しい在庫から順番に引き当てる方法。
    - 数式:
      - 引当数量 = min(注文数量, 在庫数量)
      - 引当価格 = 引当数量 × 在庫単価
    """
    remaining_quantity = order.quantity
    for inventory in reversed(inventories):
        if remaining_quantity <= 0:
            break
        allocated_quantity = min(remaining_quantity, inventory.quantity)
        remaining_quantity -= allocated_quantity
        inventory.quantity -= allocated_quantity
        create_allocation_result(db, order, allocated_quantity, allocated_quantity * inventory.unit_price)

def allocate_average(db: Session, order: Order, inventories: list[Inventory]):
    """
    平均価格戦略で在庫割り当てを実行する関数
    :param db: データベースセッション
    :param order: 割り当て対象の注文
    :param inventories: 在庫リスト

    平均引当 (Average Allocation):
    - 説明: 在庫の平均単価を使用して引き当てる方法。
    - 数式:
      - 平均単価 = (在庫数量1 × 在庫単価1 + 在庫数量2 × 在庫単価2 + ...) / (在庫数量1 + 在庫数量2 + ...)
      - 引当価格 = 注文数量 × 平均単価
    """
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
        total_allocated_price += allocated_quantity * average_price

    create_allocation_result(db, order, order.quantity, total_allocated_price)

def allocate_specific(db: Session, order: Order, inventories: list[Inventory]):
    """
    特定の在庫から割り当てを実行する関数
    :param db: データベースセッション
    :param order: 割り当て対象の注文
    :param inventories: 在庫リスト

    特定在庫引当 (Specific Allocation):
    - 説明: 特定の在庫から注文数量分を引き当てる方法。
    - 数式:
      - 引当数量 = 注文数量
      - 引当価格 = 引当数量 × 特定在庫の単価
    """
    for inventory in inventories:
        if inventory.quantity >= order.quantity:
            allocated_quantity = order.quantity
            inventory.quantity -= allocated_quantity
            create_allocation_result(db, order, allocated_quantity, allocated_quantity * inventory.unit_price)
            break

def allocate_total_average(db: Session, order: Order, inventories: list[Inventory]):
    """
    全体の平均価格で在庫割り当てを実行する関数
    :param db: データベースセッション
    :param order: 割り当て対象の注文
    :param inventories: 在庫リスト

    全体平均引当 (Total Average Allocation):
    - 説明: 全ての在庫の平均単価を使用して引き当てる方法。
    - 数式:
      - 全体平均単価 = (在庫数量1 × 在庫単価1 + 在庫数量2 × 在庫単価2 + ...) / (在庫数量1 + 在庫数量2 + ...)
      - 引当価格 = 注文数量 × 全体平均単価
    """
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

    create_allocation_result(db, order, order.quantity, order.quantity * total_average_price)

def allocate_moving_average(db: Session, order: Order, inventories: list[Inventory]):
    """
    移動平均価格で在庫割り当てを実行する関数
    :param db: データベースセッション
    :param order: 割り当て対象の注文
    :param inventories: 在庫リスト

    移動平均引当 (Moving Average Allocation):
    - 説明: 直近の一定数の在庫の平均単価を使用して引き当てる方法。
    - 数式:
      - 移動平均単価 = (直近の在庫単価1 + 直近の在庫単価2 + ...) / ウィンドウサイズ
      - 引当価格 = 注文数量 × 移動平均単価
    """
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
        moving_average_price = sum(prices) / len(prices)

    create_allocation_result(db, order, order.quantity, order.quantity * moving_average_price)

def create_allocation_result(db: Session, order: Order, allocated_quantity: int, allocated_price: float):
    """
    割り当て結果を作成する関数
    :param db: データベースセッション
    :param order: 割り当て対象の注文
    :param allocated_quantity: 割り当てた数量
    :param allocated_price: 割り当てた価格
    """
    allocation_result = AllocationResult(
        order_id=order.id,
        allocated_quantity=allocated_quantity,
        allocated_price=allocated_price
    )
    db.add(allocation_result)
    logger.info(f"Created allocation result for order {order.id} with allocated quantity {allocated_quantity} and price {allocated_price}")

def main():
    """
    メイン関数
    """
    from database import SessionLocal
    db = SessionLocal()
    strategies = ["FIFO", "LIFO", "AVERAGE", "SPECIFIC", "TOTAL_AVERAGE", "MOVING_AVERAGE"]
    for strategy in strategies:
        allocate_inventory(db, strategy)

if __name__ == "__main__":
    main()
