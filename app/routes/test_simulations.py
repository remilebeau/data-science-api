from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


# @desc test random distribution with triangular
# @route GET /api/simulations/random_values
def test_simulations_random_values_triangular():
    params = {"min": 5000, "mean": 12000, "max": 16000}
    response = client.get(
        "/api/simulations/random_values",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/random_values",
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


# @desc test random distribution with truncated normal
# @route GET /api/simulations/random_values
def test_simulations_random_values_truncated_normal():
    params = {"min": 5000, "mean": 12000, "max": 16000, "sd": 3496}
    response = client.get(
        "/api/simulations/random_values",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/random_values",
        params=params,
    )
    values = response.json()["distValues"]
    values_two = response_two.json()["distValues"]
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    assert len(values) == 1000
    # check that the correct distribution was used
    assert response.json()["distribution"] == "truncated normal"
    # check that the 1000 values are reproducible with the same inputs
    assert values == values_two
    # check that the 1000 values are not identical
    assert min(values) < max(values)


# @desc test random distribution with uniform
# @route GET /api/simulations/random_values
def test_simulations_random_values_uniform():
    params = {"min": 5000, "max": 16000}
    response = client.get(
        "/api/simulations/random_values",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/random_values",
        params=params,
    )
    values = response.json()["distValues"]
    values_two = response_two.json()["distValues"]
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    assert len(values) == 1000
    # check that the correct distribution was used
    assert response.json()["distribution"] == "uniform"
    # check that the 1000 values are reproducible with the same inputs
    assert values == values_two
    # check that the 1000 values are not identical
    assert min(values) < max(values)


# @desc test random distribution with normal
# @route GET /api/simulations/random_values
def test_simulations_random_values_normal():
    params = {"mean": 12000, "sd": 3496}
    response = client.get(
        "/api/simulations/random_values",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/random_values",
        params=params,
    )
    values = response.json()["distValues"]
    values_two = response_two.json()["distValues"]
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    assert len(values) == 1000
    # check that the correct distribution was used
    assert response.json()["distribution"] == "normal"
    # check that the 1000 values are reproducible with the same inputs
    assert values == values_two
    # check that the 1000 values are not identical
    assert min(values) < max(values)


# @desc Test production simulation with triangular distribution
# @route GET /api/simulations/production
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


# @desc Test production simulation with truncated normal distribution
# @route GET /api/simulations/production
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


# @desc Test production simulation with normal distribution
# @route GET /api/simulations/production
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


# @desc Test production simulation with uniform distribution
# @route GET /api/simulations/production
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


# @desc Test cash flow simulation with triangular distribution
# @route GET /api/simulations/cash_flow
def test_simulations_cash_flow_triangular():
    params = {
        "periodsPerYear": 12,
        "fixedCost": 100000,
        "min": 5000,
        "mean": 12000,
        "max": 16000,
        "sd": 0,
    }
    response = client.get(
        "/api/simulations/cash_flow",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/cash_flow",
        params=params,
    )
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    annual_cash_flows = response.json()["annualCashFlows"]
    annual_cash_flows_two = response_two.json()["annualCashFlows"]
    assert len(annual_cash_flows) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert annual_cash_flows == annual_cash_flows_two
    # check that the 1000 values are not identical
    assert min(annual_cash_flows) < max(annual_cash_flows)


# @desc Test cash flow simulation with truncated normal distribution
# @route GET /api/simulations/cash_flow
def test_simulations_cash_flow_truncated_normal():
    params = {
        "periodsPerYear": 12,
        "fixedCost": 100000,
        "min": 5000,
        "mean": 12000,
        "max": 16000,
        "sd": 3496,
    }
    response = client.get(
        "/api/simulations/cash_flow",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/cash_flow",
        params=params,
    )
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    annual_cash_flows = response.json()["annualCashFlows"]
    annual_cash_flows_two = response_two.json()["annualCashFlows"]
    assert len(annual_cash_flows) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert annual_cash_flows == annual_cash_flows_two
    # check that the 1000 values are not identical
    assert min(annual_cash_flows) < max(annual_cash_flows)


# @desc Test cash flow simulation with uniform distribution
# @route GET /api/simulations/cash_flow
def test_simulations_cash_flow_uniform():
    params = {
        "periodsPerYear": 12,
        "fixedCost": 100000,
        "min": 5000,
        "mean": 0,
        "max": 16000,
        "sd": 0,
    }
    response = client.get(
        "/api/simulations/cash_flow",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/cash_flow",
        params=params,
    )
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    annual_cash_flows = response.json()["annualCashFlows"]
    annual_cash_flows_two = response_two.json()["annualCashFlows"]
    assert len(annual_cash_flows) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert annual_cash_flows == annual_cash_flows_two
    # check that the 1000 values are not identical
    assert min(annual_cash_flows) < max(annual_cash_flows)


# @desc Test cash flow simulation with normal distribution
# @route GET /api/simulations/cash_flow
def test_simulations_cash_flow_normal():
    params = {
        "periodsPerYear": 12,
        "fixedCost": 100000,
        "min": 0,
        "mean": 12000,
        "max": 0,
        "sd": 3496,
    }
    response = client.get(
        "/api/simulations/cash_flow",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/cash_flow",
        params=params,
    )
    # check status code
    assert response.status_code == 200
    # check that 1000 values were returned
    annual_cash_flows = response.json()["annualCashFlows"]
    annual_cash_flows_two = response_two.json()["annualCashFlows"]
    assert len(annual_cash_flows) == 1000
    # check that the 1000 values are reproducible with the same inputs
    assert annual_cash_flows == annual_cash_flows_two
    # check that the 1000 values are not identical
    assert min(annual_cash_flows) < max(annual_cash_flows)


# @desc Test marketing simulation
# @route POST /api/simulations/marketing
def test_simulations_marketing():
    params = {
        "retentionRate": 0.85,
        "discountRate": 0.15,
        "stDev": 0.1,
        "yearOneMeanProfit": -40,
        "yearTwoMeanProfit": 60,
        "yearThreeMeanProfit": 80,
        "yearFourMeanProfit": 100,
        "yearFiveMeanProfit": 120,
    }
    response = client.get(
        "/api/simulations/marketing",
        params=params,
    )
    response_two = client.get(
        "/api/simulations/marketing",
        params=params,
    )
    # check status code
    assert response.status_code == 200
    # check that the meanNPV is reproducible with the same inputs
    mean_npv = response.json()["meanNPV"]
    mean_npv_two = response_two.json()["meanNPV"]
    assert mean_npv == mean_npv_two
