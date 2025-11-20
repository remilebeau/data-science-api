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


@router.post(
    "/production", summary="Run Monte Carlo production simulation (triangular demand)"
)
def simulation_production_triangular(inputs: SimulationInputs):
    """
    Run a Monte Carlo simulation to evaluate production profit under uncertain demand
    using a triangular distribution for demand.
    """
    if not (inputs.worstLikelyDemand < inputs.expectedDemand < inputs.bestLikelyDemand):
        raise HTTPException(
            400, "worstLikelyDemand must be < expectedDemand < bestLikelyDemand"
        )
    np.random.seed(42)

    def simulate():
        # Generate demand from triangular distribution
        demand = np.random.triangular(
            left=inputs.worstLikelyDemand,
            mode=inputs.expectedDemand,
            right=inputs.bestLikelyDemand,
        )
        sold = min(inputs.productionQuantity, demand)
        unsold = max(inputs.productionQuantity - demand, 0)
        profit = (
            sold * inputs.unitPrice
            + unsold * inputs.salvagePrice
            - inputs.productionQuantity * inputs.unitCost
            - inputs.fixedCost
        )
        return profit

    # Run 1000 Monte Carlo simulations
    profits = np.array([simulate() for _ in range(1000)])
    expected_profit = profits.mean()
    value_at_risk = float(np.percentile(profits, 5))
    best_case = float(np.percentile(profits, 95))

    return {
        **inputs.model_dump(),
        "expectedProfit": expected_profit,
        "valueAtRisk": value_at_risk,
        "bestCase": best_case,
    }
