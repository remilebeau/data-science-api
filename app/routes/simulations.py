import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class SimulationInputs(BaseModel):
    productionQuantity: float
    unitCost: float
    unitPrice: float
    salvagePrice: float
    fixedCost: float
    worstLikelyDemand: float
    expectedDemand: float
    bestLikelyDemand: float


router = APIRouter(prefix="/api/simulations", tags=["simulations"])


@router.post("/production")
def simulation_production_triangular(inputs: SimulationInputs):
    if not (inputs.worstLikelyDemand < inputs.expectedDemand < inputs.bestLikelyDemand):
        raise HTTPException(400, "Invalid demand bounds")

    np.random.seed(42)
    iterations = 5000 # Increased for smoother charts

    # VECTORIZED MATH: Generate all demand points at once
    demands = np.random.triangular(
        left=inputs.worstLikelyDemand,
        mode=inputs.expectedDemand,
        right=inputs.bestLikelyDemand,
        size=iterations
    )

    # Calculate results across the entire array
    sold = np.minimum(inputs.productionQuantity, demands)
    unsold = np.maximum(inputs.productionQuantity - demands, 0)
    profits = (
        sold * inputs.unitPrice
        + unsold * inputs.salvagePrice
        - inputs.productionQuantity * inputs.unitCost
        - inputs.fixedCost
    )

    # Statistics for the summary table
    expected_profit = float(np.mean(profits))
    value_at_risk = float(np.percentile(profits, 5))
    best_case = float(np.percentile(profits, 95))
    prob_of_loss = float(np.mean(profits < 0)) # New FinOps metric!

    # BINNED DATA FOR HISTOGRAM:
    # Instead of sending 5,000 raw numbers (slow), we send the "counts" for histogram bars.
    counts, bin_edges = np.histogram(profits, bins=30)
    
    # Format bins for Recharts: [{binCenter: 100, count: 5}, ...]
    histogram_data = [
        {"bin": float(bin_edges[i]), "count": int(counts[i])} 
        for i in range(len(counts))
    ]

    return {
        "summary": {
            "expectedProfit": expected_profit,
            "valueAtRisk": value_at_risk,
            "bestCase": best_case,
            "probOfLoss": prob_of_loss
        },
        "histogramData": histogram_data,
        "rawPoints": profits.tolist() if iterations <= 1000 else [] # Optional for scatter plots
    }
