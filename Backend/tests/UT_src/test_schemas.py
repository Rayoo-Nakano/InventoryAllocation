from fastapi.testclient import TestClient
from main import app, get_db, authenticate_token
from models import Order, Inventory, AllocationResult
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from schemas import InventoryRequest, OrderRequest
from unittest import mock

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_order():
    """
    注文の作成をテストする関数
    """
    order_data = OrderRequest(item_code="ABC123", quantity=5)
    
    with mock.patch("main.authenticate_token") as mock_authenticate_token:
        mock_authenticate_token.return_value = {"sub": "user_id", "scope": "openid"}
        
        response = client.post("/orders", json=order_data.dict())
        assert response.status_code == 200
        assert response.json()["item_code"] == "ABC123"
        assert response.json()["quantity"] == 5

def test_get_orders():
    """
    注文の取得をテストする関数
    """
    with mock.patch("main.authenticate_token") as mock_authenticate_token:
        mock_authenticate_token.return_value = {"sub": "user_id", "scope": "openid"}
        
        response = client.get("/orders")
        assert response.status_code == 200
        assert len(response.json()) > 0

def test_create_inventory():
    """
    在庫の作成をテストする関数
    """
    inventory_data = InventoryRequest(item_code="XYZ789", quantity=10, receipt_date=date(2023, 6, 1), unit_price=9.99)
    
    with mock.patch("main.authenticate_token") as mock_authenticate_token:
        mock_authenticate_token.return_value = {"sub": "user_id", "scope": "openid"}
        
        response = client.post("/inventories", json=inventory_data.dict())
        assert response.status_code == 200
        assert response.json()["item_code"] == "XYZ789"
        assert response.json()["quantity"] == 10
        assert response.json()["receipt_date"] == "2023-06-01"
        assert response.json()["unit_price"] == 9.99

def test_get_inventories():
    """
    在庫の取得をテストする関数
    """
    with mock.patch("main.authenticate_token") as mock_authenticate_token:
        mock_authenticate_token.return_value = {"sub": "user_id", "scope": "openid"}
        
        response = client.get("/inventories")
        assert response.status_code == 200
        assert len(response.json()) > 0

def test_allocate_inventory():
    """
    在庫の割り当てをテストする関数
    """
    order_data = OrderRequest(item_code="ABC123", quantity=5)
    inventory_data = InventoryRequest(item_code="ABC123", quantity=10, receipt_date=date(2023, 6, 1), unit_price=9.99)
    
    with mock.patch("main.authenticate_token") as mock_authenticate_token:
        mock_authenticate_token.return_value = {"sub": "user_id", "scope": "openid"}
        
        # 在庫を作成
        client.post("/inventories", json=inventory_data.dict())
        
        # 注文を作成
        response = client.post("/orders", json=order_data.dict())
        order_id = response.json()["order_id"]
        
        # 在庫を割り当て
        response = client.post(f"/orders/{order_id}/allocate")
        assert response.status_code == 200
        assert response.json()["allocated_quantity"] == 5
        assert response.json()["allocated_price"] == 9.99
