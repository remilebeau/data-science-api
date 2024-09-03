from fastapi.testclient import TestClient
from .utils import is_triangular, is_percent
from ..main import app

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
