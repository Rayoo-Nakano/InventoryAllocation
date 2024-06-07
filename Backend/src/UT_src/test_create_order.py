def test_create_order():
    # ケース1
    result = create_order({'items': {'item1': 5}, 'customerName': 'John'})
    assert result['status'] == 'success'
    assert 'orderId' in result
    # ケース2
    assert create_order({'customerName': 'John'}) == {'status': 'failure', 'message': 'Missing required fields'}
    # ケース3
    assert create_order({'items': {'item1': 5}}) == {'status': 'failure', 'message': 'Missing required fields'}