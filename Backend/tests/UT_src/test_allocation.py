import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, os.path.join(grandparent_dir, 'Backend', 'src'))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Order, Inventory, AllocationResult
from allocation import allocate_inventory

# テスト用のデータベースセッションを作成する
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def test_allocate_inventory_fifo():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order1 = Order(item_code="ABC123", quantity=5)
    order2 = Order(item_code="ABC123", quantity=3)
    db.add_all([order1, order2])
    
    inventory1 = Inventory(item_code="ABC123", quantity=4, unit_price=10)
    inventory2 = Inventory(item_code="ABC123", quantity=6, unit_price=12)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # FIFOでの在庫割当てテスト
    allocation_results = allocate_inventory(db, "FIFO")
    
    assert len(allocation_results) == 2
    assert allocation_results[0].order_id == order1.order_id
    assert allocation_results[0].allocated_quantity == 5
    assert allocation_results[0].allocated_price == 52
    assert allocation_results[1].order_id == order2.order_id
    assert allocation_results[1].allocated_quantity == 3
    assert allocation_results[1].allocated_price == 36
    
    db.close()

def test_allocate_inventory_lifo():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order1 = Order(item_code="XYZ789", quantity=3)
    order2 = Order(item_code="XYZ789", quantity=5)
    db.add_all([order1, order2])
    
    inventory1 = Inventory(item_code="XYZ789", quantity=6, unit_price=15)
    inventory2 = Inventory(item_code="XYZ789", quantity=4, unit_price=18)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # LIFOでの在庫割当てテスト
    allocation_results = allocate_inventory(db, "LIFO")
    
    assert len(allocation_results) == 2
    assert allocation_results[0].order_id == order1.order_id
    assert allocation_results[0].allocated_quantity == 3
    assert allocation_results[0].allocated_price == 54
    assert allocation_results[1].order_id == order2.order_id
    assert allocation_results[1].allocated_quantity == 5
    assert allocation_results[1].allocated_price == 90
    
    db.close()

def test_allocate_inventory_average():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order = Order(item_code="DEF456", quantity=6)
    db.add(order)
    
    inventory1 = Inventory(item_code="DEF456", quantity=4, unit_price=20)
    inventory2 = Inventory(item_code="DEF456", quantity=8, unit_price=22)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # AVERAGEでの在庫割当てテスト
    allocation_results = allocate_inventory(db, "AVERAGE")
    
    assert len(allocation_results) == 1
    assert allocation_results[0].order_id == order.order_id
    assert allocation_results[0].allocated_quantity == 6
    assert allocation_results[0].allocated_price == 132
    
    db.close()

def test_allocate_inventory_specific():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order = Order(item_code="GHI789", quantity=3)
    db.add(order)
    
    inventory1 = Inventory(item_code="GHI789", quantity=2, unit_price=15)
    inventory2 = Inventory(item_code="GHI789", quantity=5, unit_price=18)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # SPECIFICでの在庫割当てテスト
    allocation_results = allocate_inventory(db, "SPECIFIC")
    
    assert len(allocation_results) == 1
    assert allocation_results[0].order_id == order.order_id
    assert allocation_results[0].allocated_quantity == 3
    assert allocation_results[0].allocated_price == 54
    
    db.close()

def test_allocate_inventory_total_average():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order = Order(item_code="JKL012", quantity=7)
    db.add(order)
    
    inventory1 = Inventory(item_code="JKL012", quantity=3, unit_price=10)
    inventory2 = Inventory(item_code="MNO345", quantity=5, unit_price=12)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # TOTAL_AVERAGEでの在庫割当てテスト
    allocation_results = allocate_inventory(db, "TOTAL_AVERAGE")
    
    assert len(allocation_results) == 1
    assert allocation_results[0].order_id == order.order_id
    assert allocation_results[0].allocated_quantity == 7
    assert allocation_results[0].allocated_price == 77
    
    db.close()

def test_allocate_inventory_moving_average():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order = Order(item_code="PQR678", quantity=4)
    db.add(order)
    
    inventory1 = Inventory(item_code="PQR678", quantity=2, unit_price=25)
    inventory2 = Inventory(item_code="PQR678", quantity=3, unit_price=28)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # MOVING_AVERAGEでの在庫割当てテスト
    allocation_results = allocate_inventory(db, "MOVING_AVERAGE")
    
    assert len(allocation_results) == 1
    assert allocation_results[0].order_id == order.order_id
    assert allocation_results[0].allocated_quantity == 4
    assert allocation_results[0].allocated_price == 106
    
    db.close()

def test_allocate_inventory_insufficient_inventory():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order = Order(item_code="STU901", quantity=10)
    db.add(order)
    
    inventory = Inventory(item_code="STU901", quantity=5, unit_price=20)
    db.add(inventory)
    
    db.commit()
    
    # 在庫不足の場合のテスト
    allocation_results = allocate_inventory(db, "FIFO")
    
    assert len(allocation_results) == 1
    assert allocation_results[0].order_id == order.order_id
    assert allocation_results[0].allocated_quantity == 5
    assert allocation_results[0].allocated_price == 100
    
    db.close()

def test_allocate_inventory_invalid_method():
    db = TestingSessionLocal()
    
    with pytest.raises(ValueError):
        allocate_inventory(db, "INVALID")
    
    db.close()
