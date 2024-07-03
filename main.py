import numpy as np
import numpy_financial as npf

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


# @desc Monte Carlo simulation of planning production by Tallys Yunes. Triangular distribution. Alpha = 0.05
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

    # define demand distribution
    demand_distribution = rng.triangular(demandMin, demandMode, demandMax, 1000)

    # define simulation
    def simulation():
        # profit = revenues - costs = sales rev + salvage rev - production cost - fixed costs
        realized_demand = float(rng.choice(demand_distribution))
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


# @desc Finance example of Monte Carlo simulation by Tallys Yunes. Triangular distribution. Alpha = 0.05
# @route GET /api/simulations/finance
# @access public
@app.get("/api/simulations/finance")
def simulation_finance(
    fixedCost: float,
    demandMin: float,
    demandMode: float,
    demandMax: float,
    yearOneMargin: float,
    annualMarginDecrease: float,
    taxRate: float,
    discountRate: float,
    demandDecayMin: float,
    demandDecayMode: float,
    demandDecayMax: float,
):
    # validate data
    if not (
        demandMin <= demandMode
        and demandMode <= demandMax
        and demandMin < demandMax
        and yearOneMargin > 0
        and annualMarginDecrease >= 0
        and annualMarginDecrease < 1
        and taxRate >= 0
        and taxRate < 1
        and discountRate >= 0
        and discountRate < 1
        and demandDecayMin <= demandDecayMode
        and demandDecayMode <= demandDecayMax
        and demandDecayMin < demandDecayMax
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid data. Please check your input and try again.",
        )

    # set seed
    rng = np.random.default_rng(seed=42)

    # define demand distribution
    demand_distribution = rng.triangular(demandMin, demandMode, demandMax, 1000)

    # define demand_decay_distribution
    demand_decay_distribution = rng.triangular(
        demandDecayMin, demandDecayMode, demandDecayMax, 1000
    )

    # define simulation
    def simulation():
        # create unit_sales list, beginning with year 1
        unit_sales = [float(rng.choice(demand_distribution))]
        # add unit_sales for years 2-5
        for year in range(1, 5):
            unit_sales.append(
                unit_sales[-1] * (1 - float(rng.choice(demand_decay_distribution)))
            )
        # create unit_margin list, beginning with year 1
        unit_margins = [yearOneMargin]
        # add unit_margins for years 2-5
        for year in range(1, 5):
            unit_margins.append(unit_margins[-1] * (1 - annualMarginDecrease))
        revenue_minus_variable_cost = [
            unit_sales[year] * unit_margins[year] for year in range(5)
        ]
        depreciation = fixedCost / 5
        before_tax_profit = [
            revenue_minus_variable_cost[year] - depreciation for year in range(5)
        ]
        after_tax_profit = [
            before_tax_profit[year] * (1 - taxRate) for year in range(5)
        ]
        cash_flows = [after_tax_profit[year] + depreciation for year in range(5)]
        cash_flows.insert(0, -fixedCost)
        return round(npf.npv(discountRate, cash_flows))

    sim_values = [simulation() for _ in range(1000)]
    # generate stats
    mean = np.mean(sim_values)
    stdError = np.std(sim_values) / np.sqrt(len(sim_values))
    lowerCI = mean - 1.96 * stdError
    upperCI = mean + 1.96 * stdError
    min_profit = min(sim_values)
    max_profit = max(sim_values)
    q1 = np.quantile(sim_values, 0.25)
    q2 = np.quantile(sim_values, 0.5)
    q3 = np.quantile(sim_values, 0.75)
    p_lose_money = sum(value < 0 for value in sim_values) / len(sim_values)
    p_lose_money_lower_ci = p_lose_money - 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / len(sim_values)
    )
    p_lose_money_upper_ci = p_lose_money + 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / len(sim_values)
    )
    value_at_risk = np.quantile(sim_values, 0.05)

    return {
        "simValues": sim_values,
        "meanProfit": round(mean),
        "stdError": round(stdError),
        "lowerCI": round(lowerCI),
        "upperCI": round(upperCI),
        "minProfit": round(min_profit),
        "maxProfit": round(max_profit),
        "q1": round(q1),
        "q2": round(q2),
        "q3": round(q3),
        "pLoseMoneyLowerCI": round(p_lose_money_lower_ci, 2),
        "pLoseMoneyUpperCI": round(p_lose_money_upper_ci, 2),
        "valueAtRisk": round(value_at_risk),
    }
