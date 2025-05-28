from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_simulations_production_valid():
    body = {
        "unitCost": 80,
        "unitPrice": 100,
        "salvagePrice": 30,
        "fixedCost": 100000,
        "productionQuantity": 7800,
        "worstLikelyDemand": 5000,
        "expectedDemand": 12000,
        "bestLikelyDemand": 16000,
        "demandStandardDeviation": 3496,
    }
    res = client.post("/api/simulations/production", json=body)
    res_two = client.post("/api/simulations/production", json=body)
    assert res.status_code == 200
    profits = res.json()["simulatedProfits"]
    profits_two = res_two.json()["simulatedProfits"]
    assert profits == profits_two
    assert len(profits) == 1000
    # check we did not get the same profit 1000 times
    assert min(profits) < max(profits)
    # expected profit with these inputs should be between 47,000 and 49,000
    expectedProfit = res.json()["expectedProfit"]
    assert 47000 <= expectedProfit <= 49000


def test_simulations_production_invalid():
    body = {
        "unitCost": 80,
        "unitPrice": 100,
        "salvagePrice": 30,
        "fixedCost": 100000,
        "productionQuantity": 7800,
        "worstLikelyDemand": 5000,
        "expectedDemand": 5000,
        "bestLikelyDemand": 5000,
        "demandStandardDeviation": 3496,
    }
    res = client.post("/api/simulations/production", json=body)
    assert res.status_code == 400
