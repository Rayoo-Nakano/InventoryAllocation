def test_get_allocation_result():
    # ケース1
    allocation_id = 'abc123'
    result = get_allocation_result(allocation_id)
    assert result['status'] == 'success'
    assert result['allocationId'] == allocation_id
    # ケース2
    assert get_allocation_result('nonexistent') == {'status': 'failure', 'message': 'Allocation not found'}