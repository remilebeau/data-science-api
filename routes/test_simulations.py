from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_simulations_production():
    params = {
        "unitCost": 80,
        "unitPrice": 100,
        "salvagePrice": 30,
        "demandMin": 5000,
        "demandMode": 12000,
        "demandMax": 16000,
        "fixedCost": 100000,
        "productionQuantity": 7800,
    }
    response = client.get(
        "/api/simulations/production",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/production",
        params=params,
    )
    assert response.status_code == 200
    assert len(response.json()["simulatedProfits"]) == 1000
    assert (
        response.json()["simulatedProfits"] == response_two.json()["simulatedProfits"]
    )


# @desc Testing /api/simulations/finance with all parameters
def test_simulations_finance_all_params():
    params = {
        "fixedCost": 700000000,
        "yearOneMargin": 4000,
        "yearOneSalesMin": 50000,
        "yearOneSalesMode": 75000,
        "yearOneSalesMax": 85000,
        "annualMarginDecrease": 0.04,
        "annualSalesDecayMin": 0.05,
        "annualSalesDecayMode": 0.08,
        "annualSalesDecayMax": 0.10,
        "taxRate": 0.4,
        "discountRate": 0.1,
    }
    response = client.get(
        "/api/simulations/finance",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/finance",
        params=params,
    )
    assert response.status_code == 200
    assert len(response.json()["simulatedNPVs"]) == 1000
    assert response.json()["simulatedNPVs"] == response_two.json()["simulatedNPVs"]


"""
Testing /api/simulations/finance with only these parameters:
    fixedCost
    yearOneMargin
    yearOneSalesMin
    yearOneSalesMode
    yearOneSalesMax

The remaining parameters will be set to 0:
    annualMarginDecrease
    annualSalesDecayMin
    annualSalesDecayMode
    annualSalesDecayMax
    taxRate
    discountRate
"""


# @desc
# @route GET /api/simulations/finance
def test_simulations_finance_no_margin_some_params():
    params = {
        "fixedCost": 700000000,
        "yearOneMargin": 4000,
        "yearOneSalesMin": 50000,
        "yearOneSalesMode": 75000,
        "yearOneSalesMax": 85000,
        "annualMarginDecrease": 0,
        "annualSalesDecayMin": 0,
        "annualSalesDecayMode": 0,
        "annualSalesDecayMax": 0,
        "taxRate": 0,
        "discountRate": 0,
    }
    response = client.get(
        "/api/simulations/finance",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/finance",
        params=params,
    )
    assert response.status_code == 200
    assert len(response.json()["simulatedNPVs"]) == 1000
    assert response.json()["simulatedNPVs"] == response_two.json()["simulatedNPVs"]
