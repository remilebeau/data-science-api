from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


# @desc test random distribution with triangular
# @route GET /api/distributions/random
def test_distributions_random():
    params = {"min": 5000, "mean": 12000, "max": 16000, "sd": 0}
    response = client.get(
        "/api/distributions/random",
        params=params,
    )
    response_two = client.get(
        "/api/distributions/random",
        params=params,
    )
    values = response.json()["distValues"]
    values_two = response_two.json()["distValues"]
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    assert len(values) == 1000
    # check that the correct distribution was used
    assert response.json()["distribution"] == "triangular"
    # check that the 1000 values are reproducible with the same inputs
    assert values == values_two
    # check that the 1000 values are not identical
    assert min(values) < max(values)
