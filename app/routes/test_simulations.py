from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


# @DESC Test production simulation with triangular distribution
# @ROUTE POST /api/simulations/production
def test_simulations_production_triangular():
    body = {
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
    res = client.post("/api/simulations/production", json=body)
    res_two = client.post("/api/simulations/production", json=body)
    assert res.status_code == 200
    profits = res.json()["simulatedProfits"]
    profits_two = res_two.json()["simulatedProfits"]
    assert profits == profits_two
    assert len(profits) == 1000
    assert min(profits) < max(profits)
    # mean profit with these inputs should be between 47,000 and 49,000
    mean = res.json()["mean"]
    assert 47000 <= mean <= 49000


# @DESC Test production simulation with truncated normal distribution
# @ROUTE POST /api/simulations/production
def test_simulations_production_truncated_normal():
    body = {
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
    res = client.post("/api/simulations/production", json=body)
    res_two = client.post("/api/simulations/production", json=body)
    assert res.status_code == 200
    profits = res.json()["simulatedProfits"]
    profits_two = res_two.json()["simulatedProfits"]
    assert profits == profits_two
    assert len(profits) == 1000
    assert min(profits) < max(profits)
    # mean profit with these inputs should be between 47,000 and 49,000
    mean = res.json()["mean"]
    assert 47000 <= mean <= 49000
