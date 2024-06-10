from fastapi.testclient import TestClient
from main import app, get_db
from models import Order, Inventory, AllocationResult
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

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
    order_data = {"item_code": "ABC123", "quantity": 5}
    response = client.post("/orders", json=order_data)
    assert response.status_code == 200
    assert response.json()["item_code"] == "ABC123"
    assert response.json()["quantity"] == 5

def test_get_orders():
    response = client.get("/orders")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_create_inventory():
    inventory_data = {"item_code": "XYZ789", "quantity": 10, "receipt_date": "2023-06-01", "unit_price": 9.99}
    response = client.post("/inventories", json=inventory_data)
    assert response.status_code == 200
    assert response.json()["item_code"] == "XYZ789"
    assert response.json()["quantity"] == 10
    assert response.json()["receipt_date"] == "2023-06-01"
    assert response.json()["unit_price"] == 9.99

def test_get_inventories():
    response = client.get("/inventories")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_allocate_inventory():
    order = Order(item_code="ABC123", quantity=5)
    inventory
