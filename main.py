import numpy as np
import numpy_financial as npf

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# configure CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @desc returns 1000 random values from a triangular distribution
# @route GET /api/distributions/triangular
# @access public
@app.get("/api/distributions/triangular")
def distribution_triangular(distMin: float, distMode: float, distMax: float):
    """
    Returns 1000 pseudorandom values from a triangular distribution.

    Args:\n
        distMin (float): The minimum value of the distribution.\n
        distMode (float): The mode value of the distribution.\n
        distMax (float): The maximum value of the distribution.\n

    Returns:\n
        distValues (list): A list of 1000 pseudorandom values from a triangular distribution.

    Raises:\n
        HTTPException: If the input values do not satisfy the following conditions:
            - distMin <= distMode
            - distMode <= distMax
            - distMin < distMax
            A 400 status code and an error message are returned in this case.
    """
    # set seed
    rng = np.random.default_rng(seed=42)
    # check min <= mode and mode <= max and min < max
    if not (distMin <= distMode and distMode <= distMax and distMin < distMax):
        raise HTTPException(
            status_code=400,
            detail="Please ensure the following: 1) distMin <= distMode <= distMax 2) distMin < distMax",
        )
    # generate distribution
    distValues = rng.triangular(distMin, distMode, distMax, 1000).tolist()
    return {"distValues": distValues}


# @desc returns 1000 random values from a uniform distribution
# @route GET /api/distributions/uniform
# @access public
@app.get("/api/distributions/uniform")
def distribution_uniform(distMin: int, distMax: int):
    """
    Returns 1000 pseudorandom values from a uniform distribution.

    Args:\n
        distMin (int): The minimum value of the distribution.\n
        distMax (int): The maximum value of the distribution.\n

    Returns:\n
        distValues (list): A list of 1000 pseudorandom values from a uniform distribution.

    Raises:\n
        HTTPException: If the input values do not satisfy the following condition: distMin < distMax.
            A 400 status code and an error message are returned in this case.
    """
    # set seed
    rng = np.random.default_rng(seed=42)
    # check min < max
    if not (distMin < distMax):
        raise HTTPException(
            status_code=400,
            detail="Please ensure the following: distMin < distMax",
        )
    # generate distribution
    distValues = rng.uniform(distMin, distMax, 1000).tolist()
    return {"distValues": distValues}


# @desc returns 1000 random values from a truncated normal distribution
# @route GET /api/distributions/truncated_normal
# @access public
@app.get("/api/distributions/truncated_normal")
def distribution_truncated_normal(
    distMin: float, distMean: float, distMax: float, distSD: float
):
    """
    Returns 1000 pseudorandom values from a truncated normal distribution.

    Args:\n
        distMin (float): The minimum value of the distribution.\n
        distMean (float): The mean value of the distribution.\n
        distMax (float): The maximum value of the distribution.\n
        distSD (float): The standard deviation of the distribution.\n

    Returns:\n
        distValues (list): A list of 1000 pseudorandom values from a truncated normal distribution.

    Raises:\n
        HTTPException: If the input values do not satisfy the following conditions:
            - distMin <= distMean
            - distMean <= distMax
            - distMin < distMax
            - distSD >= 0
            A 400 status code and an error message are returned in this case.
    """
    # validate data
    if not (
        distMin <= distMean
        and distMean <= distMax
        and distMin < distMax
        and distSD >= 0
    ):
        raise HTTPException(
            status_code=400,
            detail="Please ensure the following: 1) distMin <= distMean <= distMax 2) distMin < distMax 3) distSD >= 0",
        )

    # set seed
    rng = np.random.default_rng(seed=42)

    # truncate with custom function
    def truncated_normal(min, max, mean, sd):
        value = rng.normal(mean, sd)
        if value < min or value > max:
            value = truncated_normal(min, max, mean, sd)
        return value

    # generate distribution
    distValues = [
        truncated_normal(distMin, distMax, distMean, distSD) for _ in range(0, 1000)
    ]

    return {"distValues": distValues}


# @desc Monte Carlo simulation for production planning. Triangular distribution. Alpha = 0.05
# @route GET /api/simulations/production
# @access public
@app.get("/api/simulations/production")
def simulation_production(
    unitCost: float,
    unitPrice: float,
    salvagePrice: float,
    demandMin: float,
    demandMode: float,
    demandMax: float,
    fixedCost: float,
    productionQuantity: float,
):
    """
    Simulates production and calculates various statistics based on the simulation results.

    Args:\n
        unitCost (float): The cost per unit of production.\n
        unitPrice (float): The price per unit of production.\n
        salvagePrice (float): The price per unit of salvage.\n
        demandMin (float): The minimum demand.\n
        demandMode (float): The mode of demand.\n
        demandMax (float): The maximum demand.\n
        fixedCost (float): The fixed cost.\n
        productionQuantity (float): The production quantity.\n

    Returns:\n
        simValues (list): A list of simulated production values.\n
        meanProfit (float): The mean observed profit.\n
        lowerCI (float): The lower 95% confidence interval for the mean.\n
        upperCI (float): The upper 95% confidence interval for the mean.\n
        minProfit (float): The minimum observed profit.\n
        maxProfit (float): The maximum observed profit.\n
        q1 (float): The first quartile of observed profits.\n
        q2 (float): The second quartile of observed profits.\n
        q3 (float): The third quartile of observed profits.\n
        pLoseMoneyLowerCI (float): The lower 95% confidence interval for the probability of losing money.\n
        pLoseMoneyUpperCI (float): The upper 95% confidence interval for the probability of losing money.\n

    Raises:\n
        HTTPException: If the inputs do not satisfy the following conditions:
            - demandMin <= demandMode
            - demandMode <= demandMax
            - demandMin < demandMax
            - productionQuantity > 0
            A 400 status code and an error message are returned in this case.

    """
    # validate data
    if not (
        demandMin <= demandMode
        and demandMode <= demandMax
        and demandMin < demandMax
        and productionQuantity > 0
    ):
        raise HTTPException(
            status_code=400,
            detail="Please ensure the following: 1) demandMin <= demandMode <= demandMax 2) demandMin < demandMax 3) productionQuantity > 0",
        )

    # set seed
    rng = np.random.default_rng(seed=42)

    # define demand distribution
    demand_distribution = rng.triangular(demandMin, demandMode, demandMax, 1000)

    # define simulation
    def simulation():
        # profit = revenues - costs = sales rev + salvage rev - production cost - fixed costs
        realized_demand = rng.choice(demand_distribution)
        units_sold = min(productionQuantity, realized_demand)
        units_salvaged = max(productionQuantity - realized_demand, 0)
        production_cost = productionQuantity * unitCost
        revenue_from_sales = units_sold * unitPrice
        revenue_from_salvage = units_salvaged * salvagePrice
        profit = revenue_from_sales + revenue_from_salvage - production_cost - fixedCost
        return profit

    # run 1000 simulations
    simulated_profits = [simulation() for _ in range(0, 1000)]

    # generate stats
    mean = round(np.mean(simulated_profits))
    stdError = round(np.std(simulated_profits) / np.sqrt(len(simulated_profits)))
    lowerCI = round(mean - 1.96 * stdError)
    upperCI = round(mean + 1.96 * stdError)
    min_profit = round(np.min(simulated_profits))
    max_profit = round(np.max(simulated_profits))
    q1 = round(np.percentile(simulated_profits, 25))
    q2 = round(np.percentile(simulated_profits, 50))
    q3 = round(np.percentile(simulated_profits, 75))
    p_lose_money = sum(profit < 0 for profit in simulated_profits) / len(
        simulated_profits
    )
    p_lose_money_lower_ci = round(
        p_lose_money
        - 1.96 * np.sqrt(p_lose_money * (1 - p_lose_money) / len(simulated_profits)),
        2,
    )
    p_lose_money_upper_ci = round(
        p_lose_money
        + 1.96 * np.sqrt(p_lose_money * (1 - p_lose_money) / len(simulated_profits)),
        2,
    )
    return {
        "simValues": simulated_profits,
        "meanProfit": mean,
        "lowerCI": lowerCI,
        "upperCI": upperCI,
        "minProfit": min_profit,
        "maxProfit": max_profit,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "pLoseMoneyLowerCI": p_lose_money_lower_ci,
        "pLoseMoneyUpperCI": p_lose_money_upper_ci,
    }
