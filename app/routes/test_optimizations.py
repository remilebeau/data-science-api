import pytest
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


@pytest.fixture
def test_staffing_logic_diagnostics():
    """Diagnostic test to see exactly what the model calculates for headcount."""
    payload = {
        "wage": 25.0,
        "fixed_overhead": 1000.0,
        "demand_intensity": 500.0,
        "min_service_level": 0.85,
        "current_headcount": 30.0,
    }

    response = client.post("/api/optimizations/staffing-plan", json=payload)
    assert response.status_code == 200
    data = response.json()

    optimal = data["plan"]["requiredHeadcount"]
    actual = payload["current_headcount"]
    status = data["comparison"]["isOverStaffed"]

    print(f"\nDiagnostic: Optimal HC={optimal}, Actual HC={actual}, Status={status}")

    # Logic: If we have 30 and the math says we only need ~24, we are Overstaffed.
    if actual > optimal:
        assert status
        assert data["comparison"]["potentialSavings"] > 0
    else:
        assert not status
        assert data["comparison"]["potentialSavings"] <= 0


def test_understaffed_scenario():
    """Force an understaffed scenario with very low headcount."""
    payload = {
        "wage": 25.0,
        "fixed_overhead": 1000.0,
        "demand_intensity": 800.0,  # Higher demand
        "min_service_level": 0.95,  # Higher SLA
        "current_headcount": 5.0,  # Extremely low staff
    }

    response = client.post("/api/optimizations/staffing-plan", json=payload)
    data = response.json()

    # At 800 demand/95% SLA, 5 people is definitely not enough.
    assert not data["comparison"]["isOverStaffed"]
    assert data["plan"]["headcountDelta"] > 0  # Delta says 'You need more'
