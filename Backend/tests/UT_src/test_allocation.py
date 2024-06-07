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
    order1 = Order(order_id=1, item_code="ABC123", quantity=5)
    order2 = Order(order_id=2, item_code="ABC123", quantity=3)
    db.add_all([order1, order2])

    inventory1 = Inventory(item_code="ABC123", quantity=4, unit_price=10)
    inventory2 = Inventory(item_code="ABC123", quantity=6, unit_price=12)
    db.add_all([inventory1, inventory2])

    db.commit()

    # FIFOでの在庫割当を実行
    allocate_inventory(db, "FIFO")

    # 結果の検証
    allocated_orders = db.query(Order).join(AllocationResult).filter(AllocationResult.order_id == Order.order_id).all()
    assert len(allocated_orders) == 2

    assert allocated_orders[0].item_code == "ABC123"
    assert allocated_orders[0].quantity == 5
    assert allocated_orders[0].allocation_resultss[0].allocated_quantity == 5
    assert allocated_orders[0].allocation_resultss[0].allocated_price == 11.0

    assert allocated_orders[1].item_code == "ABC123"
    assert allocated_orders[1].quantity == 3
    assert allocated_orders[1].allocation_resultss[0].allocated_quantity == 3
    assert allocated_orders[1].allocation_resultss[0].allocated_price == 12.0

    updated_inventories = db.query(Inventory).all()
    assert len(updated_inventories) == 2

    assert updated_inventories[0].item_code == "ABC123"
    assert updated_inventories[0].quantity == 0

    assert updated_inventories[1].item_code == "ABC123"
    assert updated_inventories[1].quantity == 2

    db.close()


def test_allocate_inventory_lifo():
    db = TestingSessionLocal()
    
    # テスト前にデータベースをクリーンアップ
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(AllocationResult).delete()
    db.commit()
    
    # テストデータの作成
    order1 = Order(order_id=1, item_code="XYZ789", quantity=3)
    order2 = Order(order_id=2, item_code="XYZ789", quantity=5)
    db.add_all([order1, order2])
    
    inventory1 = Inventory(item_code="XYZ789", quantity=6, unit_price=15)
    inventory2 = Inventory(item_code="XYZ789", quantity=4, unit_price=18)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # LIFOでの在庫割当を実行
    allocate_inventory(db, "LIFO")
    
    # 結果の検証
    allocated_orders = db.query(Order).join(AllocationResult).filter(AllocationResult.order_id == Order.order_id).all()
    assert len(allocated_orders) == 2

    assert allocated_orders[0].item_code == "XYZ789"
    assert allocated_orders[0].quantity == 3
    assert allocated_orders[0].allocation_results[0].allocated_quantity == 3
    assert allocated_orders[0].allocation_results[0].allocated_price == 18.0

    assert allocated_orders[1].item_code == "XYZ789"
    assert allocated_orders[1].quantity == 5
    assert allocated_orders[1].allocation_results[0].allocated_quantity == 5
    assert allocated_orders[1].allocation_results[0].allocated_price == 16.5

    updated_inventories = db.query(Inventory).all()
    assert len(updated_inventories) == 2

    assert updated_inventories[0].item_code == "XYZ789"
    assert updated_inventories[0].quantity == 6

    assert updated_inventories[1].item_code == "XYZ789"
    assert updated_inventories[1].quantity == 1
    
    db.close()


def test_allocate_inventory_average():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order = Order(order_id=1, item_code="DEF456", quantity=6)
    db.add(order)
    
    inventory1 = Inventory(item_code="DEF456", quantity=4, unit_price=20)
    inventory2 = Inventory(item_code="DEF456", quantity=8, unit_price=22)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # AVERAGEでの在庫割当を実行
    allocate_inventory(db, "AVERAGE")
    
    # 結果の検証
    allocated_orders = db.query(Order).join(AllocationResult).filter(AllocationResult.order_id == Order.order_id).all()
    assert len(allocated_orders) == 1

    assert allocated_orders[0].item_code == "DEF456"
    assert allocated_orders[0].quantity == 6
    assert allocated_orders[0].allocation_results.allocated_quantity == 6
    assert allocated_orders[0].allocation_results.allocated_price == 21.0

    updated_inventories = db.query(Inventory).all()
    assert len(updated_inventories) == 2

    assert updated_inventories[0].item_code == "DEF456"
    assert updated_inventories[0].quantity == 0

    assert updated_inventories[1].item_code == "DEF456"
    assert updated_inventories[1].quantity == 6
    
    db.close()

def test_allocate_inventory_specific():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order = Order(order_id=1, item_code="GHI789", quantity=3)
    db.add(order)
    
    inventory1 = Inventory(item_code="GHI789", quantity=2, unit_price=15)
    inventory2 = Inventory(item_code="GHI789", quantity=5, unit_price=18)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # SPECIFICでの在庫割当を実行
    allocate_inventory(db, "SPECIFIC")
    
    # 結果の検証
    allocated_orders = db.query(Order).join(AllocationResult).filter(AllocationResult.order_id == Order.order_id).all()
    assert len(allocated_orders) == 1

    assert allocated_orders[0].item_code == "GHI789"
    assert allocated_orders[0].quantity == 3
    assert allocated_orders[0].allocation_results.allocated_quantity == 3
    assert allocated_orders[0].allocation_results.allocated_price == 18.0

    updated_inventories = db.query(Inventory).all()
    assert len(updated_inventories) == 2

    assert updated_inventories[0].item_code == "GHI789"
    assert updated_inventories[0].quantity == 2

    assert updated_inventories[1].item_code == "GHI789"
    assert updated_inventories[1].quantity == 2
    
    db.close()

def test_allocate_inventory_total_average():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order = Order(order_id=1, item_code="JKL012", quantity=7)
    db.add(order)
    
    inventory1 = Inventory(item_code="JKL012", quantity=3, unit_price=10)
    inventory2 = Inventory(item_code="MNO345", quantity=5, unit_price=12)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # TOTAL_AVERAGEでの在庫割当を実行
    allocate_inventory(db, "TOTAL_AVERAGE")
    
    # 結果の検証
    allocated_orders = db.query(Order).join(AllocationResult).filter(AllocationResult.order_id == Order.order_id).all()
    assert len(allocated_orders) == 1

    assert allocated_orders[0].item_code == "JKL012"
    assert allocated_orders[0].quantity == 7
    assert allocated_orders[0].allocation_results.allocated_quantity == 7
    assert allocated_orders[0].allocation_results.allocated_price == 11.0

    updated_inventories = db.query(Inventory).all()
    assert len(updated_inventories) == 2

    assert updated_inventories[0].item_code == "JKL012"
    assert updated_inventories[0].quantity == 0

    assert updated_inventories[1].item_code == "MNO345"
    assert updated_inventories[1].quantity == 1
    
    db.close()

def test_allocate_inventory_moving_average():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order = Order(order_id=1, item_code="PQR678", quantity=4)
    db.add(order)
    
    inventory1 = Inventory(item_code="PQR678", quantity=2, unit_price=25)
    inventory2 = Inventory(item_code="PQR678", quantity=3, unit_price=28)
    db.add_all([inventory1, inventory2])
    
    db.commit()
    
    # MOVING_AVERAGEでの在庫割当を実行
    allocate_inventory(db, "MOVING_AVERAGE")
    
    # 結果の検証
    allocated_orders = db.query(Order).join(AllocationResult).filter(AllocationResult.order_id == Order.order_id).all()
    assert len(allocated_orders) == 1

    assert allocated_orders[0].item_code == "PQR678"
    assert allocated_orders[0].quantity == 4
    assert allocated_orders[0].allocation_results.allocated_quantity == 4
    assert allocated_orders[0].allocation_results.allocated_price == 26.5

    updated_inventories = db.query(Inventory).all()
    assert len(updated_inventories) == 2

    assert updated_inventories[0].item_code == "PQR678"
    assert updated_inventories[0].quantity == 0

    assert updated_inventories[1].item_code == "PQR678"
    assert updated_inventories[1].quantity == 1
    
    db.close()

def test_allocate_inventory_insufficient_inventory():
    db = TestingSessionLocal()
    
    # テストデータの作成
    order = Order(order_id=1, item_code="STU901", quantity=10)
    db.add(order)
    
    inventory = Inventory(item_code="STU901", quantity=5, unit_price=20)
    db.add(inventory)
    
    db.commit()
    
    # 在庫不足の場合のテスト
    allocate_inventory(db, "FIFO")
    
    # 結果の検証
    allocated_orders = db.query(Order).join(AllocationResult).filter(AllocationResult.order_id == Order.order_id).all()
    assert len(allocated_orders) == 1

    assert allocated_orders[0].item_code == "STU901"
    assert allocated_orders[0].quantity == 10
    assert allocated_orders[0].allocation_results.allocated_quantity == 5
    assert allocated_orders[0].allocation_results.allocated_price == 20.0

    updated_inventories = db.query(Inventory).all()
    assert len(updated_inventories) == 1

    assert updated_inventories[0].item_code == "STU901"
    assert updated_inventories[0].quantity == 0
    
    db.close()

def test_allocate_inventory_invalid_method():
    db = TestingSessionLocal()
    
    with pytest.raises(ValueError):
        allocate_inventory(db, "INVALID")
    
    db.close()
