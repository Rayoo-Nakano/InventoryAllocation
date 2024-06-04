def test_allocate_inventory():
    # ケース1
    assert allocate_inventory({'item1': 5}, {'item1': 10}) == {'status': 'success', 'allocatedItems': {'item1': 5}}
    # ケース2
    assert allocate_inventory({'item1': 5}, {'item1': 5}) == {'status': 'success', 'allocatedItems': {'item1': 5}}
    # ケース3
    assert allocate_inventory({'item1': 6}, {'item1': 5}) == {'status': 'failure', 'message': 'Insufficient inventory'}
    # ケース4
    assert allocate_inventory({'item1': 1}, {'item1': 0}) == {'status': 'failure', 'message': 'Insufficient inventory'}
    # ケース5
    assert allocate_inventory({'item1': 1}, {'item1': -1}) == {'status': 'failure', 'message': 'Insufficient inventory'}