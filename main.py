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


# utility functions for validation
def is_triangular(min: float, mode: float, max: float):
    return min <= mode and mode <= max and min < max


def is_percent(num: float):
    return num >= 0 and num <= 1


def is_all_zero(*args):
    return all(value == 0 for value in args)


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
    # validate data
    if not is_triangular(distMin, distMode, distMax):
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
    # validate data
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
    if not (is_triangular(distMin, distMean, distMax) and distSD >= 0):
        raise HTTPException(
            status_code=400,
            detail="Please ensure the following: 1) distMin <= distMean <= distMax 2) distMin < distMax 3) distSD >= 0",
        )

    # set seed
    rng = np.random.default_rng(seed=42)

    # truncate with custom function
    def truncated_normal(min, mean, max, sd):
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
    Simulates production and returns a 95% confidence interval of the expected profit, a 95% confidence interval of the probability of a negative profit, and the value at risk at the 5% level based on the simulation results. Demand follows a triangular distribution. 1000 simulations.

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
        meanProfit (float): The expected of the 1000 simulated profits.\n
        meanStandardError (float): The standard error of the expected profit.\n
        meanLowerCI (float): The lower 95% confidence interval for the expected profit.\n
        meanUpperCI (float): The upper 95% confidence interval for the expected profit.\n
        pLoseMoneyLowerCI (float): The lower 95% confidence interval for the probability of a negative profit.\n
        pLoseMoneyUpperCI (float): The upper 95% confidence interval for the probability of a negative profit.\n
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
    if not (is_triangular(demandMin, demandMode, demandMax) and productionQuantity > 0):
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
    value_at_risk = min(np.percentile(simulated_profits, 5), 0)
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
    annualMarginDecrease: float,
    annualSalesDecayMin: float,
    annualSalesDecayMode: float,
    annualSalesDecayMax: float,
    taxRate: float,
    discountRate: float,
):
    """
    Simulates a financial project and returns a 95% confidence interval of the mean NPV, a 95% confidence interval of the probability of a negative NPV, and the value at risk at the 5% level based on the simulation results. Planning horizon = 5 years. Sales and sales decay follow a triangular distribution. 1000 simulations.

    Args:\n
        fixedCost (float): The total fixed cost of the project.\n
        yearOneMargin (float): Margin in year 1.\n
        yearOneSalesMin (float): Minimum sales in year 1.\n
        yearOneSalesMode (float): Expected sales in year 1.\n
        yearOneSalesMax (float): Maximum sales in year 1.\n
        annualMarginDecrease (float): The annual margin decrease in years 2 to 5. Does not change from year to year.\n
        annualSalesDecayMin (float): The minimum annual sales decay in years 2 to 5.\n
        annualSalesDecayMode (float): The expected annual sales decay in years 2 to 5.\n
        annualSalesDecayMax (float): The maximum annual sales decay in years 2 to 5.\n
        taxRate (float): The tax rate.\n
        discountRate (float): The discount rate.\n

    Returns:\n
        simulatedNPVs (list): A list of simulated NPVs
        meanNPV (float): The mean NPV
        meanStandardError (float): The standard error of the mean NPV
        meanLowerCI (float): The lower 95% confidence interval of the mean NPV
        meanUpperCI (float): The upper 95% confidence interval of the mean NPV
        pLoseMoneyLowerCI (float): The lower 95% confidence interval of the probability of losing money
        pLoseMoneyUpperCI (float): The upper 95% confidence interval of the probability of losing money
        valueAtRisk (float): The value at risk at the 5% level

    Raises:\n
        HTTPException: If the input values do not satisfy the following conditions:
            - yearOneSales must fit a triangular distribution
            - annualMarginDecrease must be between 0 and 1
            - annualSalesDecay must fit a triangular distribution
            - taxRate must be between 0 and 1
            - discountRate must be between 0 and 1
            A 400 status code and an error message are returned in this case.
    """
    # validate data
    # yearOneSales must fit a triangular distribution
    if not is_triangular(yearOneSalesMin, yearOneSalesMode, yearOneSalesMax):
        raise HTTPException(
            status_code=400,
            detail="Please check that yearOneSalesMin <= yearOneSalesMode <= yearOneSalesMax and yearOneSalesMin < yearOneSalesMax.",
        )
    # annualMarginDecrease must be a percentage
    if not is_percent(annualMarginDecrease):
        raise HTTPException(
            status_code=400,
            detail="annualMarginDecrease must be between 0 and 1.",
        )
    # annualSalesDecay must be all zeroes or fit a triangular distribution
    if not (
        is_all_zero(annualSalesDecayMin, annualSalesDecayMode, annualSalesDecayMax)
        or is_triangular(annualSalesDecayMin, annualSalesDecayMode, annualSalesDecayMax)
    ):
        raise HTTPException(
            status_code=400,
            detail="Please check that annualSalesDecayMin <= annualSalesDecayMode <= annualSalesDecayMax and annualSalesDecayMin < annualSalesDecayMax.",
        )
    # taxRate must be a percentage
    if not is_percent(taxRate):
        raise HTTPException(
            status_code=400,
            detail="taxRate must be between 0 and 1.",
        )
    # discountRate must be a percentage
    if not is_percent(discountRate):
        raise HTTPException(
            status_code=400,
            detail="discountRate must be between 0 and 1.",
        )

    # set seed
    rng = np.random.default_rng(seed=42)

    # define demand distribution
    demand_distribution = rng.triangular(
        yearOneSalesMin, yearOneSalesMode, yearOneSalesMax, 1000
    )

    # define sales decay distribution
    # if sales decay is all zeroes, set it to [0]
    if is_all_zero(annualSalesDecayMin, annualSalesDecayMode, annualSalesDecayMax):
        annual_sales_decay_distribution = [0]
    # if sales decay is not all zeroes, set it to a triangular distribution
    else:
        annual_sales_decay_distribution = rng.triangular(
            annualSalesDecayMin, annualSalesDecayMode, annualSalesDecayMax, 1000
        )

    # define simulation
    def simulation():
        # unit sales year 1
        unit_sales = [rng.choice(demand_distribution)]
        # unit sales year 2-5
        unit_sales.extend(
            unit_sales[year - 1] * (1 - rng.choice(annual_sales_decay_distribution))
            for year in range(1, 5)
        )
        # unit margin year 1
        unit_margin = [yearOneMargin]
        # unit margin year 2-5
        unit_margin.extend(
            unit_margin[year - 1] * (1 - (annualMarginDecrease)) for year in range(1, 5)
        )
        # revenue minus variable cost for all 5 years
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
            before_tax_profit[year] * (1 - (taxRate)) for year in range(5)
        ]
        # calculate npv
        # add initial outflow in year 0
        cash_flows = [-fixedCost]
        # add cash flows in years 1-5
        cash_flows.extend([after_tax_profit[year] + depreciation for year in range(5)])
        npv = npf.npv((discountRate), cash_flows)
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
    value_at_risk = min(np.quantile(simulated_profits, 0.05), 0)

    return {
        "simulatedNPVs": simulated_profits,
        "meanNPV": mean_profit,
        "meanStandardError": mean_std_error,
        "meanLowerCI": mean_lower_ci,
        "meanUpperCI": mean_upper_ci,
        "pLoseMoneyLowerCI": p_lose_money_lower_ci,
        "pLoseMoneyUpperCI": p_lose_money_upper_ci,
        "valueAtRisk": value_at_risk,
    }
