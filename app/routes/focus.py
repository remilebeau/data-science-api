import pandas as pd
import io
import numpy as np
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from typing import cast

router = APIRouter(prefix="/api/focus", tags=["focus"])

def coalesce_series(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    """Combines multiple columns, prioritizing the first available data."""
    # Initialize as a Series to satisfy the linter
    result = pd.Series([None] * len(df), dtype="object")
    for col in columns:
        if col in df.columns:
            current = df[col].astype(object).replace({np.nan: None, "": None})
            # Use combine_first and cast back to Series
            result = cast(pd.Series, result.combine_first(current))
    return result

@router.post("/convert")
async def convert_to_focus(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents), low_memory=False)
        focus_df = pd.DataFrame()

        # 1. Attributes
        focus_df['AvailabilityZone'] = coalesce_series(df, ['availability_zone', 'AvailabilityZone']).fillna("Unknown")
        
        # FIX FOR LINE 36:
        # Wrap the numeric conversion to ensure Pyright sees it as a Series
        raw_costs = coalesce_series(df, ['line_item_unblended_cost', 'costInBillingCurrency'])
        numeric_costs = pd.to_numeric(raw_costs, errors='coerce')
        # Cast to pd.Series so Pyright allows .fillna()
        focus_df['BilledCost'] = cast(pd.Series, numeric_costs).fillna(0.0)

        # 2. Identity & Currency
        focus_df['BillingAccountId'] = coalesce_series(df, ['line_item_usage_account_id', 'billingProfileId']).fillna("Unknown")
        focus_df['BillingCurrency'] = coalesce_series(df, ['billing_currency', 'billingCurrencyCode']).fillna("USD")
        
        # 3. Date Normalization
        for target_col, source_cols in [
            ('ChargePeriodStart', ['line_item_usage_start_date', 'ChargePeriodStart']),
            ('ChargePeriodEnd', ['line_item_usage_end_date', 'ChargePeriodEnd'])
        ]:
            raw_dates = coalesce_series(df, source_cols)
            # Row-by-row mapping is type-safe and avoids vectorized ambiguity
            focus_df[target_col] = raw_dates.map(
                lambda x: pd.to_datetime(x, utc=True, errors='coerce').strftime('%Y-%m-%dT%H:%M:%SZ') 
                if pd.notnull(x) else ""
            )
        
        # 4. Taxonomy
        focus_df['ChargeCategory'] = 'Usage'
        focus_df['ServiceCategory'] = coalesce_series(df, ['product_product_family', 'serviceName']).fillna("Other")

        stream = io.StringIO()
        focus_df.to_csv(stream, index=False)
        return StreamingResponse(
            io.StringIO(stream.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=focus_data.csv"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))