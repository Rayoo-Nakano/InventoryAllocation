import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# テスト用の環境変数を設定する
os.environ["UTTESTING"] = "True"

def test_authentication_failure():
    """
    認証失敗のテスト
    """
    response = client.get("/protected-endpoint")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_api_endpoint_not_found():
    """
    APIアクセスポイント接続失敗のテスト
    """
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

def test_create_item():
    """
    商品を作成するテスト
    """
    item_data = {
        "name": "Test Item",
        "description": "This is a test item",
        "price": 9.99,
        "quantity": 10
    }
    response = client.post("/items", json=item_data)
    assert response.status_code == 200  # ダミーのステータスコードを使用
    assert "item_id" in response.json()

def test_get_item():
    """
    商品を取得するテスト
    """
    item_data = {
        "item_id": "dummy_item_id",
        "name": "Test Item",
        "description": "This is a test item",
        "price": 9.99,
        "quantity": 10
    }
    response = client.get("/items/dummy_item_id")
    assert response.status_code == 200
    assert response.json() == item_data

def test_update_item():
    """
    商品を更新するテスト
    """
    item_data = {
        "item_id": "dummy_item_id",
        "name": "Test Item",
        "description": "This is a test item",
        "price": 9.99,
        "quantity": 10
    }
    updated_item_data = {
        "name": "Updated Test Item",
        "description": "This is an updated test item",
        "price": 19.99,
        "quantity": 5
    }
    response = client.put("/items/dummy_item_id", json=updated_item_data)
    assert response.status_code == 200

    item_data.update(updated_item_data)
    assert response.json() == item_data

def test_delete_item():
    """
    商品を削除するテスト
    """
    response = client.delete("/items/dummy_item_id")
    assert response.status_code == 204

def test_create_order():
    """
    注文を作成するテスト
    """
    dummy_order_data = {
        "user_id": "test_user",
        "items": [
            {"item_id": "item1", "quantity": 2},
            {"item_id": "item2", "quantity": 1}
        ]
    }
    response = client.post("/orders", json=dummy_order_data)
    assert response.status_code == 200  # ダミーのステータスコードを使用
    assert "order_id" in response.json()

def test_get_order():
    """
    注文を取得するテスト
    """
    order_data = {
        "order_id": "dummy_order_id",
        "user_id": "test_user",
        "items": [
            {"item_id": "item1", "quantity": 2},
            {"item_id": "item2", "quantity": 1}
        ]
    }
    response = client.get("/orders/dummy_order_id")
    assert response.status_code == 200
    assert response.json() == order_data

def test_update_order():
    """
    注文を更新するテスト
    """
    order_data = {
        "order_id": "dummy_order_id",
        "user_id": "test_user",
        "items": [
            {"item_id": "item1", "quantity": 2},
            {"item_id": "item2", "quantity": 1}
        ]
    }
    updated_order_data = {
        "items": [
            {"item_id": "item1", "quantity": 3},
            {"item_id": "item3", "quantity": 2}
        ]
    }
    response = client.put("/orders/dummy_order_id", json=updated_order_data)
    assert response.status_code == 200

    order_data["items"] = updated_order_data["items"]
    assert response.json() == order_data

def test_delete_order():
    """
    注文を削除するテスト
    """
    response = client.delete("/orders/dummy_order_id")
    assert response.status_code == 204
