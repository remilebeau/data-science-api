from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_get_staffing_plan_success():
    """Test that a standard valid input returns the expected plan and comparison."""
    payload = {
        "wage": 25.0,
        "fixed_overhead": 1000.0,
        "demand_intensity": 500.0,
        "min_service_level": 0.85
    }
    
    response = client.post("/api/optimizations/staffing-plan", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check Plan structure
    assert "plan" in data
    assert data["plan"]["targetSLA"] == 85.0
    assert data["plan"]["requiredHeadcount"] > 0
    assert data["plan"]["totalCost"] > 1000.0 # Must be more than fixed overhead
    
    # Check Comparison structure
    assert "comparison" in data
    assert data["comparison"]["potentialSavings"] > 0
    assert data["comparison"]["efficiencyGain"] == 15.0

def test_high_sla_costs_more():
    """Verify that requiring a higher SLA results in higher headcount/cost."""
    low_sla_payload = {
        "wage": 25.0, "fixed_overhead": 1000.0, 
        "demand_intensity": 500.0, "min_service_level": 0.70
    }
    high_sla_payload = {
        "wage": 25.0, "fixed_overhead": 1000.0, 
        "demand_intensity": 500.0, "min_service_level": 0.95
    }
    
    res_low = client.post("/api/optimizations/staffing-plan", json=low_sla_payload).json()
    res_high = client.post("/api/optimizations/staffing-plan", json=high_sla_payload).json()
    
    assert res_high["plan"]["requiredHeadcount"] > res_low["plan"]["requiredHeadcount"]
    assert res_high["plan"]["totalCost"] > res_low["plan"]["totalCost"]

def test_invalid_input_types():
    """Ensure the API rejects bad data types (Pydantic validation)."""
    payload = {
        "wage": "not-a-number",
        "fixed_overhead": 1000.0,
        "demand_intensity": 500.0,
        "min_service_level": 0.85
    }
    response = client.post("/api/optimizations/staffing-plan", json=payload)
    assert response.status_code == 422 # Unprocessable Entity