from fastapi.testclient import TestClient
from .utils import is_triangular, is_percent, is_all_zero
from main import app

client = TestClient(app)


def test_is_triangular():
    assert is_triangular(1, 2, 3)
    assert not is_triangular(0, 0, 0)
    assert not is_triangular(3, 2, 1)
    assert not is_triangular(2, 1, 3)


def test_is_percent():
    assert is_percent(0.5)
    assert is_percent(0)
    assert is_percent(1)
    assert not is_percent(1.5)
    assert not is_percent(-0.5)


def test_is_all_zero():
    assert is_all_zero(0, 0, 0)
    assert not is_all_zero(1, 0, 0)
    assert not is_all_zero(0, 0, 1)
    assert not is_all_zero(0, 1, 0)
    assert not is_all_zero(1, 1, 1)
