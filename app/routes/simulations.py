from fastapi import APIRouter, HTTPException
import numpy as np
from ..utils.utils import generate_stats, is_triangular, is_truncated_normal

router = APIRouter(
    prefix="/api/simulations",
    tags=["simulations"],
    responses={404: {"description": "Not found"}},
)


# @desc Monte Carlo simulation for production planning
# @route GET /api/simulations/production
# @access public
@router.get("/production")
def simulation_production(
    productionQuantity: float,
    unitCost: float,
    unitPrice: float,
    salvagePrice: float,
    fixedCost: float,
    demandMin: float,
    demandMode: float,
    demandMax: float,
    demandSD: float,
):
    """
    Monte Carlo simulation for production planning

    PARAMS:

    productionQuantity: number of units to be produced\n
    unitCost: variable costs per unit\n
    unitPrice: sell price per unit\n
    salvagePrice: salvage price of units produced above demand\n
    fixedCost: fixed cost of production\n
    demandMin: minimum forecasted demand\n
    demandMode: average forecasted demand\n
    demandMax: maximum forecasted demand\n
    demandSD: standard deviation forecasted demand\n

    RETURNS:

    minimum: minimum profit\n
    valueAtRisk: 5th percentile profit\n
    q1: 25th percentile profit\n
    mean: mean profit\n
    meanLowerCI: mean profit lower 95% confidence interval\n
    meanUpperCI: mean profit upper 95% confidence interval\n
    median: 50th percentile profit\n
    q3: 75th percentile profit\n
    maximum: maximum profit\n
    pLoseMoney: probability of losing money\n
    pLoseMoneyLowerCI: probability of losing money 95% lower confidence interval\n
    pLoseMoneyUpperCI: probability of losing money 95% upper confidence interval\n
    simulatedProfits: 1000 simulated profits

    """
    # set seed
    rng = np.random.default_rng(seed=42)

    # define truncated normal function
    def truncated_normal(min: float, mean: float, max: float, sd: float) -> float:
        value = rng.normal(mean, sd)
        if value < min or value > max:
            value = truncated_normal(min, max, mean, sd)
        return value

    # define demand distribution based on provided values
    if is_triangular(demandMin, demandMode, demandMax, demandSD):
        demand_distribution = rng.triangular(demandMin, demandMode, demandMax, 1000)
    elif is_truncated_normal(demandMin, demandMode, demandMax, demandSD):
        demand_distribution = [
            truncated_normal(demandMin, demandMode, demandMax, demandSD)
            for _ in range(0, 1000)
        ]
    else:
        raise HTTPException(
            status_code=400,
            detail="Please check that (min <= mean <= max) and (min < max) and (sd >= 0)",
        )

    # define simulation
    def simulation():
        # profit = sales revenue + salvage revenue - production costs - fixed costs
        # pick a random demand value
        realized_demand: float = rng.choice(demand_distribution)
        units_sold = min(productionQuantity, realized_demand)
        units_salvaged = productionQuantity - units_sold
        production_cost = productionQuantity * unitCost
        revenue_from_sales = units_sold * unitPrice
        revenue_from_salvage = units_salvaged * salvagePrice
        profit = revenue_from_sales + revenue_from_salvage - production_cost - fixedCost
        return profit

    # run 1000 simulations
    simulated_profits = [simulation() for _ in range(0, 1000)]

    # generate stats
    (
        minimum,
        value_at_risk,
        q1,
        median,
        q3,
        maximum,
        mean_profit,
        mean_profit_lower_ci,
        mean_profit_upper_ci,
        p_lose_money,
        p_lose_money_lower_ci,
        p_lose_money_upper_ci,
    ) = generate_stats(simulated_profits)

    return {
        "minimum": minimum,
        "valueAtRisk": value_at_risk,
        "q1": q1,
        "mean": mean_profit,
        "meanLowerCI": mean_profit_lower_ci,
        "meanUpperCI": mean_profit_upper_ci,
        "median": median,
        "q3": q3,
        "maximum": maximum,
        "pLoseMoney": p_lose_money,
        "pLoseMoneyLowerCI": p_lose_money_lower_ci,
        "pLoseMoneyUpperCI": p_lose_money_upper_ci,
        "simulatedProfits": simulated_profits,
    }
