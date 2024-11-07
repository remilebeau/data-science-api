from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


# @desc Test production simulation with triangular distribution
# @route GET /api/simulations/production
def test_simulations_production_triangular():
    params = {
        "unitCost": 80,
        "unitPrice": 100,
        "salvagePrice": 30,
        "fixedCost": 100000,
        "productionQuantity": 7800,
        "demandMin": 5000,
        "demandMode": 12000,
        "demandMax": 16000,
        "demandSD": 0,
    }
    response = client.get(
        "/api/simulations/production",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/production",
        params=params,
    )
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    profits = response.json()["simulatedProfits"]
    profits_two = response_two.json()["simulatedProfits"]
    mean = response.json()["mean"]
    assert len(profits) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert profits == profits_two
    # check that the 1000 values are not identical
    assert min(profits) < max(profits)
    # check for accuracy. the mean profit with these inputs should be between 47,000 and 49,000
    assert 47000 <= mean <= 49000


# @desc Test production simulation with truncated normal distribution
# @route GET /api/simulations/production
def test_simulations_production_truncated_normal():
    params = {
        "unitCost": 80,
        "unitPrice": 100,
        "salvagePrice": 30,
        "fixedCost": 100000,
        "productionQuantity": 7800,
        "demandMin": 5000,
        "demandMode": 12000,
        "demandMax": 16000,
        "demandSD": 3496,
    }
    response = client.get(
        "/api/simulations/production",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/production",
        params=params,
    )
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    profits = response.json()["simulatedProfits"]
    profits_two = response_two.json()["simulatedProfits"]
    mean = response.json()["mean"]
    assert len(profits) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert profits == profits_two
    # check that the 1000 values are not identical
    assert min(profits) < max(profits)
    # check for accuracy. the mean profit with these inputs should be between 47,000 and 49,000
    assert 47000 <= mean <= 49000
