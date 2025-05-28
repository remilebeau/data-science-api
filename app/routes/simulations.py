from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np


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


router = APIRouter(
    prefix="/api/simulations",
    tags=["simulations"],
)


# @DESC Monte Carlo simulation for production planning
# @ROUTE POST /api/simulations/production
# @ACCESS public
@router.post("/production")
def simulation_production(inputs: SimulationInputs):
    '''
    productionQuantity = Units you will produce. You decide this today for the entire year.\n
     unitCost = Production costs per unit\n
     unitPrice = Sell price per unit\n
     salvagePrice = Salvage price per unit\n
     fixedCost = Total fixed costs for the project\n
     worstLikelyDemand = Worst likely demand (5th percentile)\n
     expectedDemand = Expected demand\n
     bestLikelyDemand = Best likely demand (95th percentile)\n
     demandStandardDeviation = Standard deviation of demand. Calculate with historical data, or estimate with a multiple of expected demand.
    '''

    # validate inputs
    if not (inputs.worstLikelyDemand < inputs.expectedDemand < inputs.bestLikelyDemand):
        raise HTTPException(
            status_code=400,
            detail="Invalid demand values. Ensure that worstLikelyDemand < expectedDemand < bestLikelyDemand",
        )
    if inputs.demandStandardDeviation <= 0:
        raise HTTPException(
            status_code=400,
            detail="demandStandardDeviation must be greater than 0",
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
            inputs.worstLikelyDemand, inputs.expectedDemand, inputs.bestLikelyDemand, inputs.demandStandardDeviation
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

    # calculate stats
    expectedProfit = np.mean(simulated_profits)
    volatility = np.std(simulated_profits)
    sharpeRatio = expectedProfit / volatility
    worstLikelyCase = np.percentile(simulated_profits, 5)
    bestLikelyCase = np.percentile(simulated_profits, 95)

    return {
        "expectedProfit": expectedProfit,
        "volatility": volatility,
        "sharpeRatio":sharpeRatio,
        "worstLikelyCase": worstLikelyCase,
        "bestLikelyCase": bestLikelyCase,
        "simulatedProfits": simulated_profits,
    }
