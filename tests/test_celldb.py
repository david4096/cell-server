import phoenixdb

import celldb.celldb as celldb


def test_connect():
    """
    Guarantees that celldb and phoenixdb connect behave similarly when given
    a bad URL.
    :return:
    """
    url = "test"
    p_exception = None
    c_exception = None
    try:
        phoenixdb.connect(url)
    except Exception as e:
        p_exception = e
    try:
        celldb.connect(url)
    except Exception as e:
        c_exception = e
    assert p_exception
    assert c_exception
    assert str(p_exception) == str(c_exception)


def test_feature_dtype_list():
    """
    Demonstrates how feature-datatype strings are created so that the client
    can easily create dynamic column queries.
    :return:
    """
    featureIds = ["A", "B", "C"]
    expected = "A DECIMAL(10, 6), B DECIMAL(10, 6), C DECIMAL(10, 6)"
    assert celldb._feature_dtype_list(featureIds) == expected


def test_safe_fn():
    """
    Shows how the safe_fn guards against all exceptions.
    :return:
    """
    assert celldb._safe_fn(pow, 2, "a") is None
