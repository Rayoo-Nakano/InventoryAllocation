def test_main():
    # ケース1
    result = main()
    assert result['allocateInventory']['status'] == 'success'
    assert result['updateInventory']['status'] == 'success'
    assert result['createOrder']['status'] == 'success'
    assert result['getAllocationResult']['status'] == 'success'