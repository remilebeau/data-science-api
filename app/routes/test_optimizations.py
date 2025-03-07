from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


# @DESC Test staffing optimization with no upper bounds on decision variables
# @ROUTE POST /api/optimizations/staffing
def test_staffing_optimization_no_max():
    body = {
        "monReq": 17,
        "tueReq": 13,
        "wedReq": 15,
        "thuReq": 19,
        "friReq": 14,
        "satReq": 16,
        "sunReq": 11,
        "x1Max": -1,
        "x2Max": -1,
        "x3Max": -1,
        "x4Max": -1,
        "x5Max": -1,
        "x6Max": -1,
        "x7Max": -1,
    }
    res = client.post("/api/optimizations/staffing", json=body)
    minStaff = res.json()["minStaff"]
    assert res.status_code == 200
    # check for accuracy. answer should be between 22 and 24
    assert 22 <= minStaff <= 24


# @DESC Test staffing optimization with upper bounds on decision variables
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
        "x1Max": -1,
        "x2Max": -1,
        "x3Max": -1,
        "x4Max": 0,
        "x5Max": -1,
        "x6Max": -1,
        "x7Max": -1,
    }
    res = client.post("/api/optimizations/staffing", json=body)
    minStaff = res.json()["minStaff"]
    assert res.status_code == 200
    # check for accuracy. answer should be between 25 and 27
    assert 25 <= minStaff <= 27
