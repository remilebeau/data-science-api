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


# @desc Monte Carlo simulation for production planning. Triangular distribution. n = 1000. α = 0.05
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
        unitCost (float): The production cost per unit.\n
        unitPrice (float): The sell price per unit.\n
        salvagePrice (float): The salvage price per unit.\n
        demandMin (float): The minimum demand.\n
        demandMode (float): The expected demand.\n
        demandMax (float): The maximum demand.\n
        fixedCost (float): The total fixed costs for the production.\n
        productionQuantity (float): The production quantity.\n

    Returns:\n
        simulatedProfits (list): A list of 1000 simulated profits.\n
        meanProfit (float): The mean of the 1000 simulated profits.\n
        meanStandardError (float): The standard error of the mean.\n
        meanLowerCI (float): The lower 95% confidence interval for the mean.\n
        meanUpperCI (float): The upper 95% confidence interval for the mean.\n
        pLoseMoneyLowerCI (float): The lower 95% confidence interval for the probability of losing money.\n
        pLoseMoneyUpperCI (float): The upper 95% confidence interval for the probability of losing money.\n
        valueAtRisk (float): The value at risk at the 5% level.\n

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
        realized_demand: float = rng.choice(demand_distribution)
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
    mean_profit = np.mean(simulated_profits)
    mean_std_error = np.std(simulated_profits) / np.sqrt(1000)
    mean_lower_ci = mean_profit - 1.96 * mean_std_error
    mean_upper_ci = mean_profit + 1.96 * mean_std_error
    p_lose_money = sum(profit < 0 for profit in simulated_profits) / 1000
    p_lose_money_lower_ci = p_lose_money - 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / 1000
    )
    p_lose_money_upper_ci = p_lose_money + 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / 1000
    )
    value_at_risk = np.percentile(simulated_profits, 5)
    return {
        "simulatedProfits": simulated_profits,
        "meanProfit": mean_profit,
        "meanStandardError": mean_std_error,
        "meanLowerCI": mean_lower_ci,
        "meanUpperCI": mean_upper_ci,
        "pLoseMoneyLowerCI": p_lose_money_lower_ci,
        "pLoseMoneyUpperCI": p_lose_money_upper_ci,
        "valueAtRisk": value_at_risk,
    }


# @desc Monte Carlo simulation for financial planning. Triangular distribution. n = 1000. α = 0.05. Planning horizon = 5 years
# @route GET /api/simulations/finance
# @access public
@app.get("/api/simulations/finance")
def simulation_finance(
    fixedCost: float,
    yearOneMargin: float,
    yearOneSalesMin: float,
    yearOneSalesMode: float,
    yearOneSalesMax: float,
    annualMarginDecrease: float | None = None,
    annualSalesDecayMin: float | None = None,
    annualSalesDecayMode: float | None = None,
    annualSalesDecayMax: float | None = None,
    taxRate: float | None = None,
    discountRate: float | None = None,
):
    """
    Monte Carlo simulation for financial planning. Triangular distribution. n = 1000. α = 0.05. Planning horizon = 5 years

    Args:\n
        fixedCost (float): The fixed cost of the project.\n
        yearOneMargin (float): Margin in year 1.\n
        yearOneSalesMin (float): Minimum sales in year 1.\n
        yearOneSalesMode (float): Expected sales in year 1.\n
        yearOneSalesMax (float): Maximum sales in year 1.\n
        annualMarginDecrease (float, optional): The annual margin decrease. Defaults to None.\n
        annualSalesDecayMin (float, optional): The minimum sales decay. Defaults to None.\n
        annualSalesDecayMode (float, optional): The expected sales decay. Defaults to None.\n
        annualSalesDecayMax (float, optional): The maximum sales decay. Defaults to None.\n
        taxRate (float, optional): The tax rate. Defaults to None.\n
        discountRate (float, optional): The discount rate. Defaults to None.\n

    Returns:\n
        simulatedNPVs (list): A list of simulated NPVs.
        meanNPV (float): The mean NPV.
        meanStandardError (float): The standard error of the mean NPV.
        meanLowerCI (float): The lower confidence interval of the mean NPV.
        meanUpperCI (float): The upper confidence interval of the mean NPV.
        pLoseMoney (float): The probability of losing money.
        pLoseMoneyLowerCI (float): The lower confidence interval of the probability of losing money.
        pLoseMoneyUpperCI (float): The upper confidence interval of the probability of losing money.
        valueAtRisk (float): The value at risk.

    Raises:\n
        HTTPException: If the input values do not satisfy the following conditions:
            - yearOneSalesMin <= yearOneSalesMode
            - yearOneSalesMode <= yearOneSalesMax
            - yearOneSalesMin < yearOneSalesMax
            - annualSalesDecayMin <= annualSalesDecayMode
            - annualSalesDecayMode <= annualSalesDecayMax
            - annualSalesDecayMin < annualSalesDecayMax
            - taxRate >= 0
            - taxRate <= 1
            - discountRate >= 0
            - discountRate <= 1
            A 400 status code and an error message are returned in this case.
    """
    # validate data
    # yearOneSales must fit a triangular distribution
    if not (
        yearOneSalesMin <= yearOneSalesMode
        and yearOneSalesMode <= yearOneSalesMax
        and yearOneSalesMin < yearOneSalesMax
    ):
        raise HTTPException(
            status_code=400,
            detail="Please check that yearOneSalesMin <= yearOneSalesMode <= yearOneSalesMax and yearOneSalesMin < yearOneSalesMax.",
        )
    # if annualMarginDecrease is provided, it must be between 0 and 1
    if not (
        annualMarginDecrease is None
        or (annualMarginDecrease >= 0 and annualMarginDecrease <= 1)
    ):
        raise HTTPException(
            status_code=400,
            detail="If annualMarginDecrease is provided, it must be between 0 and 1.",
        )
    # if annualSalesDecay is provided, it must fit a triangular distribution
    if not (
        annualSalesDecayMin is None
        or annualSalesDecayMode is None
        or annualSalesDecayMax is None
        or annualSalesDecayMin <= annualSalesDecayMode
        and annualSalesDecayMode <= annualSalesDecayMax
        and annualSalesDecayMin < annualSalesDecayMax
    ):
        raise HTTPException(
            status_code=400,
            detail="If annual sales decay is provided, please check that annualSalesDecayMin <= annualSalesDecayMode <= annualSalesDecayMax and annualSalesDecayMin < annualSalesDecayMax.",
        )
    # if taxRate is provided, it must be between 0 and 1
    if not (taxRate is None or (taxRate >= 0 and taxRate <= 1)):
        raise HTTPException(
            status_code=400,
            detail="If taxRate is provided, it must be between 0 and 1.",
        )
    # if discountRate is provided, it must be between 0 and 1
    if not (discountRate is None or (discountRate >= 0 and discountRate <= 1)):
        raise HTTPException(
            status_code=400,
            detail="If discountRate is provided, it must be between 0 and 1.",
        )

    # set seed
    rng = np.random.default_rng(seed=42)

    # define demand distribution
    demand_distribution = rng.triangular(
        yearOneSalesMin, yearOneSalesMode, yearOneSalesMax, 1000
    )

    # define sales decay distribution, if provided
    if annualSalesDecayMin and annualSalesDecayMode and annualSalesDecayMax:
        annualSalesDecayDistribution = rng.triangular(
            annualSalesDecayMin, annualSalesDecayMode, annualSalesDecayMax, 1000
        )
    else:
        annualSalesDecayDistribution = [0]

    # define simulation
    def simulation():
        # unit sales year 1
        unit_sales = [rng.choice(demand_distribution)]
        # unit sales year 2-5
        unit_sales.extend(
            unit_sales[year - 1] * (1 - rng.choice(annualSalesDecayDistribution))
            for year in range(1, 5)
        )
        # unit margin year 1
        unit_margin = [yearOneMargin]
        # unit margin year 2-5
        unit_margin.extend(
            unit_margin[year - 1] * (1 - (annualMarginDecrease or 0))
            for year in range(1, 5)
        )
        # revenue - variable cost for all 5 years
        revenue_minus_variable_cost = [
            unit_sales[year] * unit_margin[year] for year in range(5)
        ]
        # depreciation for all 5 years
        depreciation = fixedCost / 5
        # before tax profit for all 5 years
        before_tax_profit = [
            revenue_minus_variable_cost[year] - depreciation for year in range(5)
        ]
        # after tax profit for all 5 years
        after_tax_profit = [
            before_tax_profit[year] * (1 - (taxRate or 0)) for year in range(5)
        ]
        # calculate npv
        # add initial outflow in year 0
        cash_flows = [-fixedCost]
        # add cash flows in years 1-5
        cash_flows.extend([after_tax_profit[year] + depreciation for year in range(5)])
        npv = npf.npv((discountRate or 0), cash_flows)
        return npv

    # run simulation
    simulated_profits = [simulation() for _ in range(1000)]

    # generate stats
    mean_profit = np.mean(simulated_profits)
    mean_std_error = np.std(simulated_profits) / np.sqrt(1000)
    mean_lower_ci = mean_profit - 1.96 * mean_std_error
    mean_upper_ci = mean_profit + 1.96 * mean_std_error
    p_lose_money = sum([profit < 0 for profit in simulated_profits]) / 1000
    p_lose_money_lower_ci = p_lose_money - 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / 1000
    )
    p_lose_money_upper_ci = p_lose_money + 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / 1000
    )
    value_at_risk = np.quantile(simulated_profits, 0.05)

    return {
        "simulatedNPVs": simulated_profits,
        "meanNPV": mean_profit,
        "meanStandardError": mean_std_error,
        "meanLowerCI": mean_lower_ci,
        "meanUpperCI": mean_upper_ci,
        "pLoseMoney": p_lose_money,
        "pLoseMoneyLowerCI": p_lose_money_lower_ci,
        "pLoseMoneyUpperCI": p_lose_money_upper_ci,
        "valueAtRisk": value_at_risk,
    }
