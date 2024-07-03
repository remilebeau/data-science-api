import numpy as np

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()


class BootstrapDataset(BaseModel):
    values: list


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
    # validate data
    if distSD < 0:
        raise HTTPException(
            status_code=400,
            detail="Standard deviation must be non-negative",
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


# @desc monte carlo simulation of planning production by Tallys Yunes. triangular distribution instead of truncated normal. confidence intervals are 95%
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

    # simulation function
    def calculate_profit(
        unitCost: float,
        unitPrice: float,
        salvagePrice: float,
        demandMin: float,
        demandMode: float,
        demandMax: float,
        fixedCost: float,
        productionQuantity: float,
    ):
        # profit = revenues - costs = sales rev + salvage rev - production cost - fixed costs
        demand_distribution = rng.triangular(demandMin, demandMode, demandMax, 1000)
        realized_demand = float(rng.choice(demand_distribution, 1).sum())
        units_sold = min(productionQuantity, realized_demand)
        units_salvaged = max(productionQuantity - realized_demand, 0)
        production_cost = productionQuantity * unitCost
        revenue_from_sales = units_sold * unitPrice
        revenue_from_salvage = units_salvaged * salvagePrice
        profit = revenue_from_sales + revenue_from_salvage - production_cost - fixedCost
        return profit

    # run 1000 simulations
    simulated_profits = [
        calculate_profit(
            unitCost,
            unitPrice,
            salvagePrice,
            demandMin,
            demandMode,
            demandMax,
            fixedCost,
            productionQuantity,
        )
        for _ in range(0, 1000)
    ]

    # generate stats
    mean = round(np.mean(simulated_profits))
    stdError = round(1.96 * np.std(simulated_profits) / np.sqrt(len(simulated_profits)))
    lowerCI = round(mean - stdError)
    upperCI = round(mean + stdError)
    min_profit = round(np.min(simulated_profits))
    max_profit = round(np.max(simulated_profits))
    q1 = round(np.percentile(simulated_profits, 25))
    q2 = round(np.percentile(simulated_profits, 50))
    q3 = round(np.percentile(simulated_profits, 75))
    p_lose_money = [profit < 0 for profit in simulated_profits].count(True) / len(
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
        "simulatedProfits": simulated_profits,
        "meanProfit": mean,
        "stdError": stdError,
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
