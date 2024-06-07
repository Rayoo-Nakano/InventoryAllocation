import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Backend.src.main import app, get_db
from models import Base
from schemas import OrderRequest, InventoryRequest, AllocationRequest
from utils import COGNITO_JWKS_URL, COGNITO_AUDIENCE, COGNITO_ISSUER

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_authenticate_user_valid_token():
    # 有効なJWTトークンをモックする
    valid_token = "valid_token"
    response = client.post("/orders", headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200

def test_authenticate_user_invalid_token():
    invalid_token = "invalid_token"
    response = client.post("/orders", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication token"}

def test_create_order():
    order_data = {"item_code": "ABC123", "quantity": 5}
    response = client.post("/orders", json=order_data)
    assert response.status_code == 200
    assert response.json()["item_code"] == "ABC123"
    assert response.json()["quantity"] == 5

def test_get_orders():
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_inventory():
    inventory_data = {"item_code": "ABC123", "quantity": 10}
    response = client.post("/inventories", json=inventory_data)
    assert response.status_code == 200
    assert response.json()["item_code"] == "ABC123"
    assert response.json()["quantity"] == 10

def test_get_inventories():
    response = client.get("/inventories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_allocate():
    order_data = {"item_code": "ABC123", "quantity": 5}
    inventory_data = {"item_code": "ABC123", "quantity": 10}
    client.post("/orders", json=order_data)
    client.post("/inventories", json=inventory_data)
    allocation_data = {"order_id": 1, "item_code": "ABC123", "quantity": 5}
    response = client.post("/allocate", json=allocation_data)
    assert response.status_code == 200
    assert response.json()["order_id"] == 1
    assert response.json()["allocated_quantity"] == 5

def test_get_allocation_results():
    response = client.get("/allocation-results")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
