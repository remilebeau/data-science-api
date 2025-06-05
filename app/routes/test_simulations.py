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
    expectedProfitOne = res.json()["expectedProfit"]
    worstLikelyCase = res.json()["worstLikelyCase"]
    bestLikelyCase = res.json()["bestLikelyCase"]
    expectedProfitTwo = res_two.json()["expectedProfit"]
    assert expectedProfitOne == expectedProfitTwo
    # check we did not get the same profit 1000 times
    assert worstLikelyCase < bestLikelyCase
    # check for accuracy
    assert 47000 <= expectedProfitOne <= 49000


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
