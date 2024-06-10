import os
from fastapi.testclient import TestClient
from main import app
from database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import jwt

client = TestClient(app)

# テスト用のデータベースを設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    """
    テスト用のデータベース接続を提供する関数
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# テスト用の認証トークンを生成
valid_token_payload = {
    "sub": "valid_user_id",
    "name": "Valid User",
    "email": "valid@example.com"
}
invalid_token_payload = {
    "sub": "invalid_user_id",
    "name": "Invalid User",
    "email": "invalid@example.com"
}
valid_token = jwt.encode(valid_token_payload, "your_secret_key", algorithm="HS256")
invalid_token = jwt.encode(invalid_token_payload, "your_secret_key", algorithm="HS256")

def test_create_order_success():
    """
    注文作成の成功テスト
    """
    order_data = {
        "item_code": "ABC123",
        "quantity": 5
    }
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.post("/orders", json=order_data, headers=headers)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["item_code"] == order_data["item_code"]
    assert response.json()["quantity"] == order_data["quantity"]

def test_get_orders_success():
    """
    注文一覧取得の成功テスト
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.get("/orders", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_inventory_success():
    """
    在庫作成の成功テスト
    """
    inventory_data = {
        "item_code": "ABC123",
        "quantity": 10
    }
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.post("/inventories", json=inventory_data, headers=headers)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["item_code"] == inventory_data["item_code"]
    assert response.json()["quantity"] == inventory_data["quantity"]

def test_get_inventories_success():
    """
    在庫一覧取得の成功テスト
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.get("/inventories", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_allocate_success():
    """
    在庫割り当ての成功テスト
    """
    # 注文を作成
    order_data = {
        "item_code": "ABC123",
        "quantity": 5
    }
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.post("/orders", json=order_data, headers=headers)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # 在庫を作成
    inventory_data = {
        "item_code": "ABC123",
        "quantity": 10
    }
    response = client.post("/inventories", json=inventory_data, headers=headers)
    assert response.status_code == 200

    # 在庫割り当てを実行
    allocation_data = {
        "order_id": order_id,
        "item_code": "ABC123",
        "quantity": 3
    }
    response = client.post("/allocate", json=allocation_data, headers=headers)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["order_id"] == allocation_data["order_id"]
    assert response.json()["item_code"] == allocation_data["item_code"]
    assert response.json()["allocated_quantity"] == allocation_data["quantity"]

def test_get_allocation_results_success():
    """
    割り当て結果一覧取得の成功テスト
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.get("/allocation-results", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_nonexistent_endpoint():
    """
    存在しないエンドポイントへのアクセステスト
    """
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.get("/nonexistent-endpoint", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

def test_create_order_invalid_data():
    """
    無効なデータでの注文作成テスト
    """
    order_data = {
        "item_code": "",
        "quantity": -1
    }
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.post("/orders", json=order_data, headers=headers)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "ensure this value has at least 1 characters"
    assert response.json()["detail"][1]["msg"] == "ensure this value is greater than 0"

def test_authentication_failure():
    """
    認証失敗のテスト
    """
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = client.get("/orders", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "無効なトークンです"}
