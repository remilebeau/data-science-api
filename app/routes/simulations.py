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

    # validate inputs
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

    # calculate stats
    mean = np.mean(simulated_profits)
    mean_lower_ci = mean - 1.96 * np.std(simulated_profits) / np.sqrt(
        len(simulated_profits)
    )
    mean_upper_ci = mean + 1.96 * np.std(simulated_profits) / np.sqrt(
        len(simulated_profits)
    )
    p_lose_money = sum(profit < 0 for profit in simulated_profits) / len(
        simulated_profits
    )
    p_lose_money_lower_ci = p_lose_money - 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / len(simulated_profits)
    )
    p_lose_money_upper_ci = p_lose_money + 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / len(simulated_profits)
    )

    return {
        "mean": mean,
        "meanLowerCI": mean_lower_ci,
        "meanUpperCI": mean_upper_ci,
        "pLoseMoney": p_lose_money,
        "pLoseMoneyLowerCI": p_lose_money_lower_ci,
        "pLoseMoneyUpperCI": p_lose_money_upper_ci,
        "simulatedProfits": simulated_profits,
    }
