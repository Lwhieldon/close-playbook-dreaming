import audit_data


def test_synthetic_data_is_self_consistent():
    assert audit_data.main() == 0
