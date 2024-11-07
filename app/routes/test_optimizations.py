from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


# @desc Test production simulation with triangular distribution
# @route GET /api/optimizations/staffing
def test_staffing_optimization():
    params = {
        "monday": 17,
        "tuesday": 13,
        "wednesday": 15,
        "thursday": 19,
        "friday": 14,
        "saturday": 16,
        "sunday": 11,
    }
    response = client.get(
        "/api/optimizations/staffing",
        params=params,
    )
    objFuncVal = response.json()["objFuncVal"]

    # check status code
    assert response.status_code == 200
    # check for accuracy. answer should be between 22 and 24
    assert 22 <= objFuncVal <= 24
