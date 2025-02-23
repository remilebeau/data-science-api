from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np
from ..utils.utils import is_truncated_normal


class SimulationInputs(BaseModel):
    productionQuantity: float
    unitCost: float
    unitPrice: float
    salvagePrice: float
    fixedCost: float
    demandMin: float
    demandMean: float
    demandMax: float
    demandSD: float


router = APIRouter(
    prefix="/api/simulations",
    tags=["simulations"],
)


# @DESC Monte Carlo simulation for production planning
# @ROUTE POST /api/simulations/production
# @ACCESS public
@router.post("/production")
def simulation_production(inputs: SimulationInputs):

    if not is_truncated_normal(
        inputs.demandMin, inputs.demandMean, inputs.demandMax, inputs.demandSD
    ):
        raise HTTPException(
            status_code=400,
            detail="Please check that (min <= mean <= max) and (min < max) and (sd >= 0)",
        )

    # set seed
    rng = np.random.default_rng(seed=42)

    # define truncated normal function
    def truncated_normal(min: float, mean: float, max: float, sd: float) -> float:
        value = rng.normal(mean, sd)
        if value < min or value > max:
            value = truncated_normal(min, max, mean, sd)
        return value

    demand_distribution = [
        truncated_normal(
            inputs.demandMin, inputs.demandMean, inputs.demandMax, inputs.demandSD
        )
        for _ in range(0, 1000)
    ]

    # define simulation
    def simulation():
        # profit = salesRevenue + salvageRevenue - productionCosts - fixedCosts
        realized_demand: float = rng.choice(demand_distribution)
        units_sold = min(inputs.productionQuantity, realized_demand)
        units_salvaged = inputs.productionQuantity - units_sold
        production_cost = inputs.productionQuantity * inputs.unitCost
        revenue_from_sales = units_sold * inputs.unitPrice
        revenue_from_salvage = units_salvaged * inputs.salvagePrice
        profit = (
            revenue_from_sales
            + revenue_from_salvage
            - production_cost
            - inputs.fixedCost
        )
        return profit

    # run 1000 simulations
    simulated_profits = [simulation() for _ in range(0, 1000)]

    return {
        "minimum": np.min(simulated_profits),
        "q1": np.percentile(simulated_profits, 25),
        "mean": np.mean(simulated_profits),
        "median": np.median(simulated_profits),
        "q3": np.percentile(simulated_profits, 75),
        "maximum": np.max(simulated_profits),
        "pLoseMoney": sum(profit < 0 for profit in simulated_profits)
        / len(simulated_profits),
        "simulatedProfits": simulated_profits,
    }
