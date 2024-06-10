import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, os.path.join(grandparent_dir, 'Backend', 'src'))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from main import app, get_db
from models import Base
from jose import jwt
from utils import COGNITO_JWKS_URL, COGNITO_AUDIENCE, COGNITO_ISSUER

# テスト用の環境変数を設定する
os.environ["TESTING"] = "True"

# テスト用のデータベースセッションを作成する
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
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

def generate_test_token():
    """
    テスト用のJWTトークンを生成する関数
    :return: JWTトークン
    """
    payload = {
        "sub": "test_user",
        "aud": COGNITO_AUDIENCE,
        "iss": COGNITO_ISSUER
    }
    token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
    return token

def test_create_order_with_auth():
    """
    認証トークンを使用して注文を作成するテスト
    """
    token = generate_test_token()
    order_data = {"item_code": "ABC123", "quantity": 5}
    response = client.post("/orders", json=order_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["item_code"] == "ABC123"
    assert response.json()["quantity"] == 5

def test_create_order_without_auth():
    """
    認証トークンなしで注文を作成するテスト
    """
    order_data = {"item_code": "ABC123", "quantity": 5}
    response = client.post("/orders", json=order_data)
    assert response.status_code == 403

def test_get_orders_with_auth():
    """
    認証トークンを使用して注文一覧を取得するテスト
    """
    token = generate_test_token()
    response = client.get("/orders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_orders_without_auth():
    """
    認証トークンなしで注文一覧を取得するテスト
    """
    response = client.get("/orders")
    assert response.status_code == 403

def test_create_inventory_with_auth():
    """
    認証トークンを使用して在庫を作成するテスト
    """
    token = generate_test_token()
    inventory_data = {"item_code": "ABC123", "quantity": 10}
    response = client.post("/inventories", json=inventory_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["item_code"] == "ABC123"
    assert response.json()["quantity"] == 10

def test_create_inventory_without_auth():
    """
    認証トークンなしで在庫を作成するテスト
    """
    inventory_data = {"item_code": "ABC123", "quantity": 10}
    response = client.post("/inventories", json=inventory_data)
    assert response.status_code == 403

def test_get_inventories_with_auth():
    """
    認証トークンを使用して在庫一覧を取得するテスト
    """
    token = generate_test_token()
    response = client.get("/inventories", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_inventories_without_auth():
    """
    認証トークンなしで在庫一覧を取得するテスト
    """
    response = client.get("/inventories")
    assert response.status_code == 403

def test_allocate_with_auth():
    """
    認証トークンを使用して在庫の割り当てを行うテスト
    """
    token = generate_test_token()
    order_data = {"item_code": "ABC123", "quantity": 5}
    inventory_data = {"item_code": "ABC123", "quantity": 10}
    client.post("/orders", json=order_data, headers={"Authorization": f"Bearer {token}"})
    client.post("/inventories", json=inventory_data, headers={"Authorization": f"Bearer {token}"})
    allocation_data = {"order_id": 1, "item_code": "ABC123", "quantity": 5}
    response = client.post("/allocate", json=allocation_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["order_id"] == 1
    assert response.json()["allocated_quantity"] == 5

def test_allocate_without_auth():
    """
    認証トークンなしで在庫の割り当てを行うテスト
    """
    allocation_data = {"order_id": 1, "item_code": "ABC123", "quantity": 5}
    response = client.post("/allocate", json=allocation_data)
    assert response.status_code == 403

def test_get_allocation_results_with_auth():
    """
    認証トークンを使用して割り当て結果一覧を取得するテスト
    """
    token = generate_test_token()
    response = client.get("/allocation-results", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_allocation_results_without_auth():
    """
    認証トークンなしで割り当て結果一覧を取得するテスト
    """
    response = client.get("/allocation-results")
    assert response.status_code == 403
