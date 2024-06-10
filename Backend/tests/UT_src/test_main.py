import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# テスト用の環境変数を設定する
os.environ["UTTESTING"] = "True"

def test_create_item_unauthorized():
    """
    認証なしで商品を作成するテスト（失敗するテストケース）
    """
    item_data = {
        "name": "Test Item",
        "description": "This is a test item",
        "price": 9.99,
        "quantity": 10
    }
    response = client.post("/items", json=item_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

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
    assert response.status_code == 201
    assert "item_id" in response.json()

def test_get_item():
    """
    商品を取得するテスト
    """
    item_data = {
        "name": "Test Item",
        "description": "This is a test item",
        "price": 9.99,
        "quantity": 10
    }
    create_response = client.post("/items", json=item_data)
    item_id = create_response.json()["item_id"]

    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == item_data["name"]
    assert get_response.json()["description"] == item_data["description"]
    assert get_response.json()["price"] == item_data["price"]
    assert get_response.json()["quantity"] == item_data["quantity"]

def test_update_item():
    """
    商品を更新するテスト
    """
    item_data = {
        "name": "Test Item",
        "description": "This is a test item",
        "price": 9.99,
        "quantity": 10
    }
    create_response = client.post("/items", json=item_data)
    item_id = create_response.json()["item_id"]

    updated_item_data = {
        "name": "Updated Test Item",
        "description": "This is an updated test item",
        "price": 19.99,
        "quantity": 5
    }
    update_response = client.put(f"/items/{item_id}", json=updated_item_data)
    assert update_response.status_code == 200

    get_response = client.get(f"/items/{item_id}")
    assert get_response.json()["name"] == updated_item_data["name"]
    assert get_response.json()["description"] == updated_item_data["description"]
    assert get_response.json()["price"] == updated_item_data["price"]
    assert get_response.json()["quantity"] == updated_item_data["quantity"]

def test_delete_item():
    """
    商品を削除するテスト
    """
    item_data = {
        "name": "Test Item",
        "description": "This is a test item",
        "price": 9.99,
        "quantity": 10
    }
    create_response = client.post("/items", json=item_data)
    item_id = create_response.json()["item_id"]

    delete_response = client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404

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
    assert response.status_code == 201
    assert "order_id" in response.json()

def test_get_order():
    """
    注文を取得するテスト
    """
    order_data = {
        "user_id": "test_user",
        "items": [
            {"item_id": "item1", "quantity": 2},
            {"item_id": "item2", "quantity": 1}
        ]
    }
    create_response = client.post("/orders", json=order_data)
    order_id = create_response.json()["order_id"]

    get_response = client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    assert get_response.json()["user_id"] == order_data["user_id"]
    assert len(get_response.json()["items"]) == len(order_data["items"])
    for i in range(len(order_data["items"])):
        assert get_response.json()["items"][i]["item_id"] == order_data["items"][i]["item_id"]
        assert get_response.json()["items"][i]["quantity"] == order_data["items"][i]["quantity"]

def test_update_order():
    """
    注文を更新するテスト
    """
    order_data = {
        "user_id": "test_user",
        "items": [
            {"item_id": "item1", "quantity": 2},
            {"item_id": "item2", "quantity": 1}
        ]
    }
    create_response = client.post("/orders", json=order_data)
    order_id = create_response.json()["order_id"]

    updated_order_data = {
        "items": [
            {"item_id": "item1", "quantity": 3},
            {"item_id": "item3", "quantity": 2}
        ]
    }
    update_response = client.put(f"/orders/{order_id}", json=updated_order_data)
    assert update_response.status_code == 200

    get_response = client.get(f"/orders/{order_id}")
    assert len(get_response.json()["items"]) == len(updated_order_data["items"])
    for i in range(len(updated_order_data["items"])):
        assert get_response.json()["items"][i]["item_id"] == updated_order_data["items"][i]["item_id"]
        assert get_response.json()["items"][i]["quantity"] == updated_order_data["items"][i]["quantity"]

def test_delete_order():
    """
    注文を削除するテスト
    """
    order_data = {
        "user_id": "test_user",
        "items": [
            {"item_id": "item1", "quantity": 2},
            {"item_id": "item2", "quantity": 1}
        ]
    }
    create_response = client.post("/orders", json=order_data)
    order_id = create_response.json()["order_id"]

    delete_response = client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/orders/{order_id}")
    assert get_response.status_code == 404
