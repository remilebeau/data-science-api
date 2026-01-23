import io

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_mixed_data():
    """CSV with mixed headers and mixed date formats. No spaces after commas."""
    headers = "availability_zone,line_item_unblended_cost,line_item_usage_start_date,AvailabilityZone,costInBillingCurrency,ChargePeriodStart"
    aws_row = "us-east-1a,50.0,2026-01-01 00:00:00,,,"
    azure_row = ",,,azure-zone-1,150.0,2026-01-01T12:00:00Z"
    return f"{headers}\n{aws_row}\n{azure_row}"


def test_full_normalization_cycle(mock_mixed_data):
    response = client.post(
        "/api/focus/convert", files={"file": ("test.csv", mock_mixed_data, "text/csv")}
    )
    assert response.status_code == 200

    # Read response. Use keep_default_na=False to avoid '' becoming NaN
    df = pd.read_csv(io.StringIO(response.text), keep_default_na=False)

    # Verify BilledCost (casting because read_csv with keep_default_na=False may keep them as strings)
    assert float(df["BilledCost"].iloc[0]) == 50.0
    assert float(df["BilledCost"].iloc[1]) == 150.0

    # Verify Dates - These should now pass!
    assert df["ChargePeriodStart"].iloc[0] == "2026-01-01T00:00:00Z"
    assert df["ChargePeriodStart"].iloc[1] == "2026-01-01T12:00:00Z"

    # Verify Zones
    assert df["AvailabilityZone"].iloc[0] == "us-east-1a"
    assert df["AvailabilityZone"].iloc[1] == "azure-zone-1"
