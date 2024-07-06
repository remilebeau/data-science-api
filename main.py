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
        dict: A dictionary containing the generated distribution values.\n
            - distValues (list): A list of 1000 pseudorandom values from a triangular distribution.

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
        dict: A dictionary containing the generated distribution values.
            - distValues (list): A list of 1000 pseudorandom values from a uniform distribution.

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
        dict: A dictionary containing the generated distribution values.
            - distValues (list): A list of 1000 pseudorandom values from a truncated normal distribution.

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


# @desc Monte Carlo simulation for production planning. Credit to Tallys Yunes for the idea. Triangular distribution. Alpha = 0.05
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
        dict: A dictionary containing the simulation results, including the simulated profits, mean profit, a 95% confidence interval for the mean profit, minimum profit, maximum profit, quartiles, and a 95% confidence interval for the probability of losing money.

    Raises:\n
        HTTPException: If the input data is invalid.

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


# @desc Monte Carlo simulation for finance. Credit to Tallys Yunes for the idea. Triangular distribution. Alpha = 0.05
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
    """
    Perform a Monte Carlo simulation for finance.

    Args:\n
        fixedCost (float): The fixed cost of the project, split over 5 years using the straight-line depreciation method.\n
        demandMin (float): The minimum demand for the product.\n
        demandMode (float): The mean demand for the product.\n
        demandMax (float): The maximum demand for the product.\n
        yearOneMargin (float): The margin for the first year.\n
        annualMarginDecrease (float): The annual decrease in margin.\n
        taxRate (float): The tax rate applied to profits.\n
        discountRate (float): The discount rate used in the NPV calculation.\n
        demandDecayMin (float): The minimum demand decay.\n
        demandDecayMode (float): The mode of the demand decay distribution.\n
        demandDecayMax (float): The maximum demand decay.\n

    Returns:\n
        dict: A dictionary containing the simulation results, including the following keys:
            - simValues (List[float]): The list of simulated profits.
            - meanProfit (float): The mean profit.
            - lowerCI (float): The lower confidence interval.
            - upperCI (float): The upper confidence interval.
            - minProfit (float): The minimum profit.
            - maxProfit (float): The maximum profit.
            - q1 (float): The first quartile.
            - q2 (float): The second quartile.
            - q3 (float): The third quartile.
            - pLoseMoneyLowerCI (float): The lower confidence interval for the probability of losing money.
            - pLoseMoneyUpperCI (float): The upper confidence interval for the probability of losing money.
    """
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
        unit_sales = [rng.choice(demand_distribution)]
        # add unit_sales for years 2-5
        for year in range(1, 5):
            unit_sales.append(
                unit_sales[-1] * (1 - rng.choice(demand_decay_distribution))
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
        # insert today's outflows at [0] according to npf.npv requirements
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

    return {
        "simValues": sim_values,
        "meanProfit": round(mean),
        "lowerCI": round(lowerCI),
        "upperCI": round(upperCI),
        "minProfit": round(min_profit),
        "maxProfit": round(max_profit),
        "q1": round(q1),
        "q2": round(q2),
        "q3": round(q3),
        "pLoseMoneyLowerCI": round(p_lose_money_lower_ci, 2),
        "pLoseMoneyUpperCI": round(p_lose_money_upper_ci, 2),
    }
