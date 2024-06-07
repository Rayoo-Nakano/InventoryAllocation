def test_update_inventory():
    # ケース1
    assert update_inventory({'item1': 10}) == {'status': 'success'}
    # ケース2
    assert update_inventory({'item1': -5}) == {'status': 'failure', 'message': 'Invalid inventory amount'}