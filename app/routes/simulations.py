from fastapi import APIRouter, HTTPException
import numpy as np
from ..utils.utils import (
    generate_stats,
    determine_distribution,
)

router = APIRouter(
    prefix="/api/simulations",
    tags=["simulations"],
    responses={404: {"description": "Not found"}},
)


# @desc returns 1000 pseudorandom values
# @route GET /api/simulations/random_values
# @access public
@router.get("/random_values")
def simulation_random_values(
    min: float = 0, mean: float = 0, max: float = 0, sd: float = 0
):
    """
    Returns 1000 pseudorandom values based on the given parameters.
    The parameters must fit a triangular, normal, uniform, or truncated normal distribution.\n

    Args:\n
        min (float): The minimum value of the distribution.\n
        mean (float): The mean of the distribution.\n
        max (float): The maximum value of the distribution.\n
        sd (float): The standard deviation of the distribution.\n

    Returns:\n
        distValues (list): A list of 1000 pseudorandom values based on the given parameters.\n
        distribution (str): The distribution used to generate the values.\n

    Raises:\n
        HTTPException: If the inputs do not satisfy one of the following sets of conditions:

        triangular:
            min <= mean <= max
            min < max
            sd = 0

        normal:
            sd > 0
            min = 0
            max = 0

        truncated normal:
            min <= mean <= max
            min < max
            sd > 0

        uniform:
            min < max
            mean = 0
            sd = 0
    """
    rng = np.random.default_rng(seed=42)

    # custom function for truncated normal
    def truncated_normal(min, mean, max, sd):
        value = rng.normal(mean, sd)
        if value < min or value > max:
            value = truncated_normal(min, max, mean, sd)
        return value

    distribution = determine_distribution(min, mean, max, sd)
    if distribution == "normal":
        values = rng.normal(mean, sd, 1000).tolist()
        return {"distribution": distribution, "distValues": values}
    elif distribution == "uniform":
        values = rng.uniform(min, max, 1000).tolist()
        return {"distribution": distribution, "distValues": values}
    elif distribution == "triangular":
        values = rng.triangular(min, mean, max, 1000).tolist()
        return {"distribution": distribution, "distValues": values}
    elif distribution == "truncated normal":
        values = [truncated_normal(min, mean, max, sd) for _ in range(1000)]
        return {"distribution": distribution, "distValues": values}
    else:
        raise HTTPException(status_code=400, detail="unknown distribution")


# @desc Monte Carlo simulation for production planning
# @route GET /api/simulations/production
# @access public
@router.get("/production")
def simulation_production(
    unitCost: float = 0,
    unitPrice: float = 0,
    salvagePrice: float = 0,
    fixedCost: float = 0,
    productionQuantity: float = 0,
    demandMin: float = 0,
    demandMode: float = 0,
    demandMax: float = 0,
    demandSD: float = 0,
):
    """
    Simulates production and returns expected profit, the probability of losing money, and the 5% value at risk. Demand can follow a triangular, truncated normal, uniform, or normal distribution. α = 0.05. n = 1000.

    Args:\n
        unitCost (float): The production cost per unit.\n
        unitPrice (float): The sell price per unit.\n
        salvagePrice (float): The salvage price per unit.\n
        demandMin (float): The minimum demand.\n
        demandMode (float): The expected demand.\n
        demandMax (float): The maximum demand.\n
        demandSD (float): The standard deviation of demand.\n
        fixedCost (float): The total fixed costs for the production.\n
        productionQuantity (float): The production quantity.\n


    Returns:\n
        simulatedProfits (list): A list of 1000 simulated profits.\n
        meanProfit (float): The expected profit.\n
        meanStandardError (float): The standard error of the expected profit.\n
        meanLowerCI (float): The lower 95% confidence interval for the expected profit.\n
        meanUpperCI (float): The upper 95% confidence interval for the expected profit.\n
        pLoseMoneyLowerCI (float): The lower 95% confidence interval for the probability of a negative profit.\n
        pLoseMoneyUpperCI (float): The upper 95% confidence interval for the probability of a negative profit.\n
        valueAtRisk (float): The value at risk at the 5% level. Returns 0 if value at risk is positive.\n

    Raises:\n
        HTTPException: If the inputs do not satisfy one of the following sets of conditions:

            triangular distribution:
                demandMin <= demandMode <= demandMax
                demandMin < demandMax
                demandSD = 0

            normal distribution:
                demandMin = 0
                demandMax = 0
                demandSD > 0

            truncated normal distribution:
                demandMin <= demandMode <= demandMax
                demandMin < demandMax
                demandSD > 0

            uniform distribution:
                demandMin < demandMax
                demandMode = 0
                demandSD = 0

            A 400 status code and an error message are returned in this case.

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
    distribution = determine_distribution(demandMin, demandMode, demandMax, demandSD)
    if distribution == "triangular":
        demand_distribution = rng.triangular(demandMin, demandMode, demandMax, 1000)
    elif distribution == "normal":
        demand_distribution = rng.normal(demandMax, demandSD, 1000)
    elif distribution == "uniform":
        demand_distribution = rng.uniform(demandMin, demandMax, 1000)
    elif distribution == "truncated normal":
        demand_distribution = [
            truncated_normal(demandMin, demandMode, demandMax, demandSD)
            for _ in range(0, 1000)
        ]
    else:
        raise HTTPException(
            status_code=400,
            detail="The provided inputs must follow one of these distributions: 1) truncated normal 2) triangular 3) uniform 4) normal",
        )

    # define simulation
    def simulation():
        # profit = revenues - costs = sales rev + salvage rev - production cost - fixed costs
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
        mean_profit,
        mean_std_error,
        mean_lower_ci,
        mean_upper_ci,
        p_lose_money_lower_ci,
        p_lose_money_upper_ci,
        value_at_risk,
    ) = generate_stats(simulated_profits).values()

    return {
        "meanProfit": mean_profit,
        "meanStandardError": mean_std_error,
        "meanLowerCI": mean_lower_ci,
        "meanUpperCI": mean_upper_ci,
        "pLoseMoneyLowerCI": p_lose_money_lower_ci,
        "pLoseMoneyUpperCI": p_lose_money_upper_ci,
        "valueAtRisk": value_at_risk,
        "simulatedProfits": simulated_profits,
    }
