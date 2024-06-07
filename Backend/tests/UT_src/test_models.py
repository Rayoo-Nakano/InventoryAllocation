import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, os.path.join(grandparent_dir, 'Backend', 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Order, Inventory, AllocationResult

# テスト用のデータベースセッションを作成する
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def test_create_order():
    db = TestingSessionLocal()
    
    order = Order(item_code="ABC123", quantity=5)
    db.add(order)
    db.commit()
    
    retrieved_order = db.query(Order).filter(Order.item_code == "ABC123").first()
    assert retrieved_order.item_code == "ABC123"
    assert retrieved_order.quantity == 5
    
    db.close()

def test_create_inventory():
    db = TestingSessionLocal()
    
    inventory = Inventory(item_code="XYZ789", quantity=10, unit_price=20)
    db.add(inventory)
    db.commit()
    
    retrieved_inventory = db.query(Inventory).filter(Inventory.item_code == "XYZ789").first()
    assert retrieved_inventory.item_code == "XYZ789"
    assert retrieved_inventory.quantity == 10
    assert retrieved_inventory.unit_price == 20
    
    db.close()

def test_create_allocation_result():
    db = TestingSessionLocal()
    
    order = Order(item_code="DEF456", quantity=3)
    db.add(order)
    db.commit()
    
    allocation_result = AllocationResult(
        order_id=order.order_id,
        item_code="DEF456",
        allocated_quantity=3,
        allocated_price=60,
        allocation_date="2023-06-08"
    )
    db.add(allocation_result)
    db.commit()
    
    retrieved_allocation_result = db.query(AllocationResult).filter(AllocationResult.order_id == order.order_id).first()
    assert retrieved_allocation_result.order_id == order.order_id
    assert retrieved_allocation_result.item_code == "DEF456"
    assert retrieved_allocation_result.allocated_quantity == 3
    assert retrieved_allocation_result.allocated_price == 60
    assert str(retrieved_allocation_result.allocation_date) == "2023-06-08"
    
    db.close()

def test_order_relationship():
    db = TestingSessionLocal()
    
    order = Order(item_code="GHI789", quantity=2)
    db.add(order)
    db.commit()
    
    allocation_result = AllocationResult(
        order_id=order.order_id,
        item_code="GHI789",
        allocated_quantity=2,
        allocated_price=40,
        allocation_date="2023-06-08"
    )
    db.add(allocation_result)
    db.commit()
    
    retrieved_order = db.query(Order).filter(Order.order_id == order.order_id).first()
    assert len(retrieved_order.allocation_results) == 1
    assert retrieved_order.allocation_results[0].item_code == "GHI789"
    
    db.close()
