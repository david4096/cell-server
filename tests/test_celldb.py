from celldb.client import client as celldb


def test_safe_fn():
    """
    Shows how the safe_fn guards against all exceptions.
    :return:
    """
    assert celldb._safe_fn(pow, 2, "a") is None
