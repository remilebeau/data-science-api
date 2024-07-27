from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


# @desc test /api/simulations/production with triangular distribution
def test_simulations_production_triangular():
    params = {
        "unitCost": 80,
        "unitPrice": 100,
        "salvagePrice": 30,
        "demandMin": 5000,
        "demandMode": 12000,
        "demandMax": 16000,
        "demandSD": 0,
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
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    profits = response.json()["simulatedProfits"]
    profits_two = response_two.json()["simulatedProfits"]
    mean_profit = response.json()["meanProfit"]
    assert len(profits) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert profits == profits_two
    # check that the 1000 values are not identical
    assert min(profits) < max(profits)
    # check for accuracy. the mean profit with these inputs should be between 47,000 and 49,000
    assert 47000 <= mean_profit <= 49000


# @desc test /api/simulations/production with truncated normal distribution
def test_simulations_production_truncated_normal():
    params = {
        "unitCost": 80,
        "unitPrice": 100,
        "salvagePrice": 30,
        "demandMin": 5000,
        "demandMode": 12000,
        "demandMax": 16000,
        "fixedCost": 100000,
        "productionQuantity": 7800,
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
    mean_profit = response.json()["meanProfit"]
    assert len(profits) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert profits == profits_two
    # check that the 1000 values are not identical
    assert min(profits) < max(profits)
    # check for accuracy. the mean profit with these inputs should be between 47,000 and 49,000
    assert 47000 <= mean_profit <= 49000


# @desc test /api/simulations/production with normal distribution
def test_simulations_production_normal():
    params = {
        "unitCost": 80,
        "unitPrice": 100,
        "salvagePrice": 30,
        "demandMin": 0,
        "demandMode": 12000,
        "demandMax": 0,
        "fixedCost": 100000,
        "productionQuantity": 7800,
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
    mean_profit = response.json()["meanProfit"]
    assert len(profits) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert profits == profits_two
    # check that the 1000 values are not identical
    assert min(profits) < max(profits)


# @desc test /api/simulations/production with uniform distribution
def test_simulations_production_uniform():
    params = {
        "unitCost": 80,
        "unitPrice": 100,
        "salvagePrice": 30,
        "demandMin": 5000,
        "demandMode": 0,
        "demandMax": 16000,
        "fixedCost": 100000,
        "productionQuantity": 7800,
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
    mean_profit = response.json()["meanProfit"]
    assert len(profits) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert profits == profits_two
    # check that the 1000 values are not identical
    assert min(profits) < max(profits)


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
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    npvs = response.json()["simulatedNPVs"]
    npvs_two = response_two.json()["simulatedNPVs"]
    mean_npv = response.json()["meanNPV"]
    assert len(npvs) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert npvs == npvs_two
    # check that the 1000 values are not identical
    assert min(npvs) < max(npvs)
    # check the simulation for accuracy. The mean NPV with these inputs should be between 30,000,000 and 32,000,000
    assert 30000000 <= mean_npv <= 32000000


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


# @route GET /api/simulations/finance
def test_simulations_finance_some_params():
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
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    npvs = response.json()["simulatedNPVs"]
    npvs_two = response_two.json()["simulatedNPVs"]
    assert len(npvs) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert npvs == npvs_two
    # check that the 1000 values are not identical
    assert min(npvs) < max(npvs)

    # @route GET /api/simulations/marketing
    params = {
        "retentionRate": 0.85,
        "discountRate": 0.15,
    }
    body = {
        "mean_profits": [
            -40,
            66,
            72,
            79,
            87,
            92,
            96,
            99,
            103,
            106,
            111,
            116,
            120,
            124,
            130,
            137,
            142,
            148,
            155,
            161,
            161,
            161,
            161,
            161,
            161,
            161,
            161,
            161,
            161,
            161,
        ]
    }
    response = client.post(
        "/api/simulations/marketing",
        params=params,
        json=body,
    )
    response_two = client.post(
        "/api/simulations/marketing",
        params=params,
        json=body,
    )
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    npvs = response.json()["simulatedNPVs"]
    npvs_two = response_two.json()["simulatedNPVs"]
    assert len(npvs) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert npvs == npvs_two
    # check that the 1000 values are not identical
    assert min(npvs) < max(npvs)
