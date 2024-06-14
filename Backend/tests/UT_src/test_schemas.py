from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from models import Base

# テスト用のデータベースURLを設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# テスト用のデータベースエンジンを作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テスト用のデータベースにテーブルを作成
Base.metadata.create_all(bind=engine)

# テスト用のデータベースセッションを作成
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# アプリケーションのデータベースセッションをテスト用のセッションでオーバーライド
app.dependency_overrides[get_db] = override_get_db

# テスト用のクライアントを作成
client = TestClient(app)

# 注文の作成テスト
def test_create_order():
    response = client.post(
        "/orders/",
        json={"customer_id": 1, "product_id": 1, "quantity": 5},
    )
    assert response.status_code == 201
    assert response.json()["customer_id"] == 1
    assert response.json()["product_id"] == 1
    assert response.json()["quantity"] == 5

# 注文の取得テスト
def test_get_orders():
    response = client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()) > 0

# 在庫の作成テスト
def test_create_inventory():
    response = client.post(
        "/inventories/",
        json={"product_id": 1, "quantity": 100},
    )
    assert response.status_code == 201
    assert response.json()["product_id"] == 1
    assert response.json()["quantity"] == 100

# 在庫の取得テスト
def test_get_inventories():
    response = client.get("/inventories/")
    assert response.status_code == 200
    assert len(response.json()) > 0

# 在庫の割り当てテスト
def test_allocate_inventory():
    # 在庫を作成
    client.post(
        "/inventories/",
        json={"product_id": 1, "quantity": 100},
    )

    # 注文を作成
    order_response = client.post(
        "/orders/",
        json={"customer_id": 1, "product_id": 1, "quantity": 5},
    )
    order_id = order_response.json()["id"]

    # 在庫を割り当て
    response = client.post(f"/orders/{order_id}/allocate")
    assert response.status_code == 200
    assert response.json()["allocated_quantity"] == 5

# 無効な注文データの作成テスト
def test_create_invalid_order():
    response = client.post(
        "/orders/",
        json={"customer_id": 1, "product_id": 1, "quantity": -5},
    )
    assert response.status_code == 400

# 存在しない注文の取得テスト
def test_get_nonexistent_order():
    response = client.get("/orders/999")
    assert response.status_code == 404

# 無効な在庫データの作成テスト
def test_create_invalid_inventory():
    response = client.post(
        "/inventories/",
        json={"product_id": 1, "quantity": -100},
    )
    assert response.status_code == 400

# 在庫不足の割り当てテスト
def test_allocate_insufficient_inventory():
    # 注文を作成
    order_response = client.post(
        "/orders/",
        json={"customer_id": 1, "product_id": 1, "quantity": 200},
    )
    order_id = order_response.json()["id"]

    # 在庫を割り当て
    response = client.post(f"/orders/{order_id}/allocate")
    assert response.status_code == 400