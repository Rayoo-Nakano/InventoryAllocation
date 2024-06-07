import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

from datetime import datetime
from pydantic import ValidationError
from schemas import (
    TokenPayload,
    OrderRequest,
    InventoryRequest,
    AllocationRequest,
    OrderResponse,
    InventoryResponse,
    AllocationResultResponse,
)

def test_token_payload():
    payload_data = {
        "sub": "user_id",
        "cognito_username": "test_user",
        "email": "test@example.com",
        "email_verified": True,
        "given_name": "John",
        "family_name": "Doe",
        "roles": ["admin", "user"],
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_example",
        "aud": "client_id",
        "exp": 1623456789,
        "iat": 1623456789,
    }
    token_payload = TokenPayload(**payload_data)
    assert token_payload.sub == "user_id"
    assert token_payload.cognito_username == "test_user"
    assert token_payload.email == "test@example.com"
    assert token_payload.email_verified is True
    assert token_payload.given_name == "John"
    assert token_payload.family_name == "Doe"
    assert token_payload.roles == ["admin", "user"]
    assert token_payload.iss == "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_example"
    assert token_payload.aud == "client_id"
    assert token_payload.exp == 1623456789
    assert token_payload.iat == 1623456789

def test_order_request():
    order_data = {"item_code": "ABC123", "quantity": 5}
    order_request = OrderRequest(**order_data)
    assert order_request.item_code == "ABC123"
    assert order_request.quantity == 5

def test_inventory_request():
    inventory_data = {"item_code": "XYZ789", "quantity": 10}
    inventory_request = InventoryRequest(**inventory_data)
    assert inventory_request.item_code == "XYZ789"
    assert inventory_request.quantity == 10

def test_allocation_request():
    allocation_data = {"order_id": 1, "item_code": "DEF456", "quantity": 3}
    allocation_request = AllocationRequest(**allocation_data)
    assert allocation_request.order_id == 1
    assert allocation_request.item_code == "DEF456"
    assert allocation_request.quantity == 3

def test_order_response():
    order_data = {"id": 1, "item_code": "GHI789", "quantity": 2}
    order_response = OrderResponse(**order_data)
    assert order_response.id == 1
    assert order_response.item_code == "GHI789"
    assert order_response.quantity == 2

def test_inventory_response():
    inventory_data = {"id": 1, "item_code": "JKL012", "quantity": 8}
    inventory_response = InventoryResponse(**inventory_data)
    assert inventory_response.id == 1
    assert inventory_response.item_code == "JKL012"
    assert inventory_response.quantity == 8

def test_allocation_result_response():
    allocation_data = {
        "id": 1,
        "order_id": 1,
        "item_code": "MNO345",
        "allocated_quantity": 4,
        "allocation_date": datetime(2023, 6, 8),
    }
    allocation_result_response = AllocationResultResponse(**allocation_data)
    assert allocation_result_response.id == 1
    assert allocation_result_response.order_id == 1
    assert allocation_result_response.item_code == "MNO345"
    assert allocation_result_response.allocated_quantity == 4
    assert allocation_result_response.allocation_date == datetime(2023, 6, 8)

def test_invalid_order_request():
    invalid_order_data = {"item_code": "ABC123", "quantity": "invalid"}
    with pytest.raises(ValidationError):
        OrderRequest(**invalid_order_data)

def test_invalid_inventory_request():
    invalid_inventory_data = {"item_code": 123, "quantity": 10}
    with pytest.raises(ValidationError):
        InventoryRequest(**invalid_inventory_data)

def test_invalid_allocation_request():
    invalid_allocation_data = {"order_id": "invalid", "item_code": "DEF456", "quantity": 3}
    with pytest.raises(ValidationError):
        AllocationRequest(**invalid_allocation_data)
