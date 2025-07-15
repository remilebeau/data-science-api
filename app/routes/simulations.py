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
    demandStandardDeviation: float


router = APIRouter(prefix="/api/simulations", tags=["simulations"])


@router.post("/production", summary="Run Monte Carlo production simulation")
def simulation_production(inputs: SimulationInputs):
    """
    Run a Monte Carlo simulation to evaluate production profit under uncertain demand.

    Simulates 1,000 demand scenarios from a truncated normal distribution and returns
    expected profit, volatility, Sharpe ratio, and 5th/95th percentile profit outcomes.
    """
    if not (inputs.worstLikelyDemand < inputs.expectedDemand < inputs.bestLikelyDemand):
        raise HTTPException(
            400, "worstLikelyDemand must be < expectedDemand < bestLikelyDemand"
        )
    if inputs.demandStandardDeviation <= 0:
        raise HTTPException(400, "demandStandardDeviation must be > 0")

    np.random.seed(42)

    def truncated_normal():
        while True:
            val = np.random.normal(
                inputs.expectedDemand, inputs.demandStandardDeviation
            )
            if inputs.worstLikelyDemand <= val <= inputs.bestLikelyDemand:
                return val

    def simulate():
        demand = truncated_normal()
        sold = min(inputs.productionQuantity, demand)
        unsold = max(inputs.productionQuantity - demand, 0)
        return (
            sold * inputs.unitPrice
            + unsold * inputs.salvagePrice
            - inputs.productionQuantity * inputs.unitCost
            - inputs.fixedCost
        )

    profits = np.array([simulate() for _ in range(1000)])
    volatility = profits.std()
    expected_profit = profits.mean()
    return {
        **inputs.model_dump(),
        "expectedProfit": expected_profit,
        "volatility": volatility,
        "sharpeRatio": expected_profit / volatility if volatility else 0,
        "worstLikelyCase": float(np.percentile(profits, 5)),
        "bestLikelyCase": float(np.percentile(profits, 95)),
    }
