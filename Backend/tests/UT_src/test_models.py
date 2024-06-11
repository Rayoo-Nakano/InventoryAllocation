import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, os.path.join(grandparent_dir, 'Backend', 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Order, Inventory, AllocationResult
from datetime import date

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
        order_id=order.id,
        item_code="DEF456",
        allocated_quantity=3,
        allocated_price=60,
        allocation_date=date(2023, 6, 8)
    )
    db.add(allocation_result)
    db.commit()

    result = db.query(AllocationResult).filter(AllocationResult.order_id == order.id).first()
    assert result.item_code == "DEF456"
    assert result.allocated_quantity == 3
    assert result.allocated_price == 60
    assert result.allocation_date == date(2023, 6, 8)
    
    db.close()

def test_order_relationship():
    db = TestingSessionLocal()
    
    order = Order(item_code="GHI789", quantity=2)
    db.add(order)
    db.commit()
    
    allocation_result = AllocationResult(
        order_id=order.id,
        item_code="GHI789",
        allocated_quantity=2,
        allocated_price=40,
        allocation_date=date(2023, 6, 8)
    )
    db.add(allocation_result)
    db.commit()
    
    retrieved_order = db.query(Order).filter(Order.id == order.id).first()
    assert len(retrieved_order.allocation_results) == 1
    assert retrieved_order.allocation_results[0].item_code == "GHI789"
    assert retrieved_order.allocation_results[0].allocated_quantity == 2
    assert retrieved_order.allocation_results[0].allocated_price == 40
    assert retrieved_order.allocation_results[0].allocation_date == date(2023, 6, 8)
    
    db.close()
