from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


# @DESC Test production simulation with triangular distribution
# @ROUTE POST /api/optimizations/staffing
def test_staffing_optimization():
    body = {
        "monReq": 17,
        "tueReq": 13,
        "wedReq": 15,
        "thuReq": 19,
        "friReq": 14,
        "satReq": 16,
        "sunReq": 11,
        "x1Max": "i",
        "x2Max": "i",
        "x3Max": "i",
        "x4Max": "i",
        "x5Max": "i",
        "x6Max": "i",
        "x7Max": "i",
    }
    res = client.post("/api/optimizations/staffing", json=body)
    minStaff = res.json()["minStaff"]
    assert res.status_code == 200
    # check for accuracy. answer should be between 22 and 24
    assert 22 <= minStaff <= 24
