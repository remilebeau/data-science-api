import pytest
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


@pytest.fixture
def valid_inputs():
    return {
        "productionQuantity": 100,
        "unitCost": 50,
        "unitPrice": 100,
        "salvagePrice": 20,
        "fixedCost": 500,
        "worstLikelyDemand": 50,
        "expectedDemand": 100,
        "bestLikelyDemand": 150,
    }


def test_simulation_success(valid_inputs):
    """Verify that a standard simulation returns correct summary keys and histogram bins."""
    response = client.post("/api/simulations/production", json=valid_inputs)

    assert response.status_code == 200
    data = response.json()

    # Check Summary Metrics
    summary = data["summary"]
    assert "expectedProfit" in summary
    assert "probOfLoss" in summary
    assert isinstance(summary["expectedProfit"], float)

    # Check Histogram Data
    assert len(data["histogramData"]) == 30
    assert "bin" in data["histogramData"][0]
    assert "count" in data["histogramData"][0]


def test_invalid_demand_bounds(valid_inputs):
    """Verify that bad triangular bounds (e.g., worst > expected) trigger a 400 error."""
    bad_inputs = valid_inputs.copy()
    bad_inputs["worstLikelyDemand"] = 200  # Logic break: Worst > Expected

    response = client.post("/api/simulations/production", json=bad_inputs)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid demand bounds"


def test_financial_logic_direction():
    """Verify that increasing price increases expected profit (Sensitivity test)."""
    base_inputs = {
        "productionQuantity": 100,
        "unitCost": 50,
        "unitPrice": 100,
        "salvagePrice": 20,
        "fixedCost": 500,
        "worstLikelyDemand": 80,
        "expectedDemand": 100,
        "bestLikelyDemand": 120,
    }

    # Run simulation with standard price
    res_low = client.post("/api/simulations/production", json=base_inputs).json()

    # Run simulation with higher price
    base_inputs["unitPrice"] = 150
    res_high = client.post("/api/simulations/production", json=base_inputs).json()

    assert res_high["summary"]["expectedProfit"] > res_low["summary"]["expectedProfit"]


def test_vectorized_math_determinism(valid_inputs):
    """Because of np.random.seed(42), the output should be identical for identical inputs."""
    res1 = client.post("/api/simulations/production", json=valid_inputs).json()
    res2 = client.post("/api/simulations/production", json=valid_inputs).json()

    assert res1["summary"]["expectedProfit"] == res2["summary"]["expectedProfit"]
