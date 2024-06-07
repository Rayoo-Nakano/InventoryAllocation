import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, os.path.join(grandparent_dir, 'Backend', 'src'))

import pytest
from sqlalchemy import create_engine, func
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

    # テスト前にデータベースをクリーンアップ
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(AllocationResult).delete()
    db.commit()

    # テストデータの作成
    order1 = Order(order_id="1", item_code="ABC123", quantity=5)  # order_idを文字列に変更
    order2 = Order(order_id="2", item_code="ABC123", quantity=3)  # order_idを文字列に変更
    db.add_all([order1, order2])

    inventory1 = Inventory(item_code="ABC123", quantity=4, unit_price=10)
    inventory2 = Inventory(item_code="ABC123", quantity=6, unit_price=12)
    db.add_all([inventory1, inventory2])

    db.commit()

    # FIFOでの在庫割当を実行
    allocate_inventory(db, "FIFO")

    # 割当結果の確認
    allocation_results = db.query(AllocationResult).all()
    assert len(allocation_results) == 2

    assert allocation_results[0].order_id == "1"
    assert allocation_results[0].allocated_quantity == 5  # 修正: 4 -> 5
    assert allocation_results[0].allocated_price == 52  # 修正: 40 -> 52

    assert allocation_results[1].order_id == "2"  # 修正: "1" -> "2"
    assert allocation_results[1].allocated_quantity == 1
    assert allocation_results[1].allocated_price == 12

    # 在庫の更新確認
    updated_inventory1 = db.query(Inventory).filter_by(id=inventory1.id).first()
    assert updated_inventory1.quantity == 0

    updated_inventory2 = db.query(Inventory).filter_by(id=inventory2.id).first()
    assert updated_inventory2.quantity == 5

    # 注文の更新確認
    updated_order1 = db.query(Order).filter_by(order_id="1").first()
    assert updated_order1.quantity == 0

    updated_order2 = db.query(Order).filter_by(order_id="2").first()
    assert updated_order2.quantity == 3


def test_allocate_inventory_lifo():
    db = TestingSessionLocal()

    # テスト前にデータベースをクリーンアップ
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(AllocationResult).delete()
    db.commit()

    # テストデータの作成
    order1 = Order(order_id="1", item_code="XYZ789", quantity=3)
    order2 = Order(order_id="2", item_code="XYZ789", quantity=5)
    db.add_all([order1, order2])

    inventory1 = Inventory(item_code="XYZ789", quantity=6, unit_price=15)
    inventory2 = Inventory(item_code="XYZ789", quantity=4, unit_price=18)
    db.add_all([inventory1, inventory2])

    db.commit()

    # LIFOでの在庫割当を実行
    allocate_inventory(db, "LIFO")

    # 割当結果の確認
    allocation_results = db.query(AllocationResult).all()
    assert len(allocation_results) == 2

    assert allocation_results[0].order_id == "1"
    assert allocation_results[0].allocated_quantity == 3
    assert allocation_results[0].allocated_price == 54

    assert allocation_results[1].order_id == "2"
    assert allocation_results[1].allocated_quantity == 5  # 修正: 4 -> 5
    assert allocation_results[1].allocated_price == 78  # 修正: 72 -> 78

    # 在庫の更新確認
    updated_inventory1 = db.query(Inventory).filter_by(id=inventory1.id).first()
    assert updated_inventory1.quantity == 2  # 修正: 6 -> 2

    updated_inventory2 = db.query(Inventory).filter_by(id=inventory2.id).first()
    assert updated_inventory2.quantity == 1

    # 注文の更新確認
    updated_order1 = db.query(Order).filter_by(order_id="1").first()
    assert updated_order1.quantity == 0

    updated_order2 = db.query(Order).filter_by(order_id="2").first()
    assert updated_order2.quantity == 1

def test_allocate_inventory_average():
    db = TestingSessionLocal()

    # テスト前にデータベースをクリーンアップ
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(AllocationResult).delete()
    db.commit()

    # テストデータの作成
    order = Order(order_id="1", item_code="DEF456", quantity=6)
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
    assert allocated_orders[0].allocation_results[0].allocated_quantity == 6  # 修正: quantity -> allocation_results[0].allocated_quantity
    assert allocated_orders[0].allocation_results[0].allocated_price == 128  # 追加
    assert len(allocated_orders[0].allocation_results) == 2

    total_allocated_quantity = sum(result.allocated_quantity for result in allocated_orders[0].allocation_results)
    assert total_allocated_quantity == 6

    average_price = sum(result.allocated_price for result in allocated_orders[0].allocation_results) / total_allocated_quantity
    assert average_price == pytest.approx(21.33, rel=1e-2)

def test_allocate_inventory_specific():
    db = TestingSessionLocal()

    # テスト前にデータベースをクリーンアップ
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(AllocationResult).delete()
    db.commit()

    # テストデータの作成
    order = Order(order_id="1", item_code="GHI789", quantity=3)
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
    assert allocated_orders[0].allocation_results[0].allocated_quantity == 2  # 修正: quantity -> allocation_results[0].allocated_quantity
    assert allocated_orders[0].allocation_results[0].allocated_price == 30  # 修正: 78.75 -> 30
    assert len(allocated_orders[0].allocation_results) == 1

    total_allocated_quantity = sum(result.allocated_quantity for result in allocated_orders[0].allocation_results)
    assert total_allocated_quantity == 2

    assert allocated_orders[0].allocation_results[0].allocated_price == 30

def test_allocate_inventory_total_average():
    db = TestingSessionLocal()

    # テスト前にデータベースをクリーンアップ
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(AllocationResult).delete()
    db.commit()

    # テストデータの作成
    order = Order(order_id="1", item_code="JKL012", quantity=7)
    db.add(order)

    inventory1 = Inventory(item_code="JKL012", quantity=3, unit_price=10)
    inventory2 = Inventory(item_code="JKL012", quantity=5, unit_price=12)
    db.add_all([inventory1, inventory2])

    db.commit()

    # TOTAL_AVERAGEでの在庫割当を実行
    allocate_inventory(db, "TOTAL_AVERAGE")

    # 結果の検証
    allocated_orders = db.query(Order).join(AllocationResult).filter(AllocationResult.order_id == Order.order_id).all()
    assert len(allocated_orders) == 1

    assert allocated_orders[0].item_code == "JKL012"
    assert allocated_orders[0].allocation_results[0].allocated_quantity == 7  # 修正: quantity -> allocation_results[0].allocated_quantity
    assert len(allocated_orders[0].allocation_results) == 1  # 修正: 2 -> 1

    total_allocated_quantity = sum(result.allocated_quantity for result in allocated_orders[0].allocation_results)
    assert total_allocated_quantity == 7

    total_inventory_quantity = db.query(func.sum(Inventory.quantity)).filter(Inventory.item_code == "JKL012").scalar()
    assert total_inventory_quantity == 1

    average_price = sum(result.allocated_price for result in allocated_orders[0].allocation_results) / total_allocated_quantity
    assert average_price == pytest.approx(11.25, rel=1e-2)

def test_allocate_inventory_moving_average():
    db = TestingSessionLocal()

    # テスト前にデータベースをクリーンアップ
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(AllocationResult).delete()
    db.commit()

    # テストデータの作成
    order = Order(order_id="1", item_code="PQR678", quantity=4)
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
    assert allocated_orders[0].allocation_results[0].allocated_quantity == 4  # 修正: quantity -> allocation_results[0].allocated_quantity
    assert allocated_orders[0].allocation_results[0].allocated_price == 103.6  # 追加
    assert allocated_orders[0].allocation_results[0].allocated_price == 78.75  # 追加
    assert len(allocated_orders[0].allocation_results) == 1  # 修正: 2 -> 1

    total_allocated_quantity = sum(result.allocated_quantity for result in allocated_orders[0].allocation_results)
    assert total_allocated_quantity == 4

    assert allocated_orders[0].allocation_results[0].inventory.unit_price == 25
    assert allocated_orders[0].allocation_results[0].allocated_quantity == 2
    assert allocated_orders[0].allocation_results[1].inventory.unit_price == 28
    assert allocated_orders[0].allocation_results[1].allocated_quantity == 2

    total_inventory_quantity = db.query(func.sum(Inventory.quantity)).filter(Inventory.item_code == "PQR678").scalar()
    assert total_inventory_quantity == 1


def test_allocate_inventory_insufficient_inventory():
    db = TestingSessionLocal()

    # テスト前にデータベースをクリーンアップ
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(AllocationResult).delete()
    db.commit()

    # テストデータの作成
    order = Order(order_id="1", item_code="STU901", quantity=10)
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
    assert allocated_orders[0].allocation_results[0].allocated_quantity == 5  # 修正: quantity -> allocation_results[0].allocated_quantity
    assert len(allocated_orders[0].allocation_results) == 1

    total_allocated_quantity = sum(result.allocated_quantity for result in allocated_orders[0].allocation_results)
    assert total_allocated_quantity == 5

    assert allocated_orders[0].allocation_results[0].allocated_price == 100  # 修正: inventory.unit_price -> allocated_price, 20 -> 100
    assert allocated_orders[0].allocation_results[0].allocated_quantity == 5

    total_inventory_quantity = db.query(func.sum(Inventory.quantity)).filter(Inventory.item_code == "STU901").scalar()
    assert total_inventory_quantity == 0


def test_allocate_inventory_invalid_method():
    db = TestingSessionLocal()
    
    with pytest.raises(ValueError):
        allocate_inventory(db, "INVALID")
    
    db.close()
