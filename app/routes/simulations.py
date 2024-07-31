from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np
import numpy_financial as npf
from ..utils.utils import is_triangular, is_percent, is_all_zero, generate_stats

router = APIRouter(
    prefix="/api/simulations",
    tags=["simulations"],
    responses={404: {"description": "Not found"}},
)


class MeanProfits(BaseModel):
    meanProfits: list[float]


# @desc Monte Carlo simulation for production planning
# @route GET /api/simulations/production
# @access public
@router.get("/production")
def simulation_production(
    unitCost: float,
    unitPrice: float,
    salvagePrice: float,
    demandMin: float,
    demandMode: float,
    demandMax: float,
    demandSD: float,
    fixedCost: float,
    productionQuantity: float,
):
    """
    Simulates production and returns common stats used in Monte Carlo simulation. The values for demandMin, demandMode, demandMax, and demandSD determine the distribution of demand.

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
    # truncated normal distribution
    if is_triangular(demandMin, demandMode, demandMax) and demandSD > 0:
        demand_distribution = [
            truncated_normal(demandMin, demandMode, demandMax, demandSD)
            for _ in range(0, 1000)
        ]
    # triangular distribution
    elif is_triangular(demandMin, demandMode, demandMax) and demandSD == 0:
        demand_distribution = rng.triangular(demandMin, demandMode, demandMax, 1000)
    # uniform distribution
    elif demandMode == 0 and demandSD == 0 and demandMin < demandMax:
        demand_distribution = rng.uniform(demandMin, demandMax, 1000)
    # normal distribution
    elif demandMin == 0 and demandMax == 0 and demandSD > 0:
        demand_distribution = rng.normal(demandMax, demandSD, 1000)
    # else raise exception
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
        "simulatedProfits": simulated_profits,
        "meanProfit": mean_profit,
        "meanStandardError": mean_std_error,
        "meanLowerCI": mean_lower_ci,
        "meanUpperCI": mean_upper_ci,
        "pLoseMoneyLowerCI": p_lose_money_lower_ci,
        "pLoseMoneyUpperCI": p_lose_money_upper_ci,
        "valueAtRisk": value_at_risk,
    }


# @desc Monte Carlo simulation for financial planning
# @route GET /api/simulations/finance
# @access public
@router.get("/finance")
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
    Simulates a financial project and returns a 95% confidence interval of the expected NPV, a 95% confidence interval of the probability of a negative NPV, and the value at risk at the 5% level based on the simulation results. Planning horizon = 5 years. Sales and sales decay follow a triangular distribution. 1000 simulations.

    Args:\n
        fixedCost (float): The total fixed cost of the project.\n
        yearOneMargin (float): Margin in year 1.\n
        yearOneSalesMin (float): Minimum sales in year 1.\n
        yearOneSalesMode (float): Expected sales in year 1.\n
        yearOneSalesMax (float): Maximum sales in year 1.\n
        annualMarginDecrease (float): The annual margin decrease in years 2 to 5. Does not change from year to year. Set to 0 to remove from model.\n
        annualSalesDecayMin (float): The minimum annual sales decay in years 2 to 5. Set annualSalesDecayMin, annualSalesDecayMode, and annualSalesDecayMax all to 0 remove from model.\n
        annualSalesDecayMode (float): The expected annual sales decay in years 2 to 5. Set annualSalesDecayMin, annualSalesDecayMode, and annualSalesDecayMax all to 0 remove from model.\n
        annualSalesDecayMax (float): The maximum annual sales decay in years 2 to 5. Set annualSalesDecayMin, annualSalesDecayMode, and annualSalesDecayMax all to 0 remove from model.\n
        taxRate (float): The tax rate. Set to 0 to remove from model.\n
        discountRate (float): The discount rate. Set to 0 to remove from model.\n

    Returns:\n
        simulatedNPVs (list): A list of simulated NPVs
        meanNPV (float): The mean NPV
        meanStandardError (float): The standard error of the mean NPV
        meanLowerCI (float): The lower 95% confidence interval of the mean NPV
        meanUpperCI (float): The upper 95% confidence interval of the mean NPV
        pLoseMoneyLowerCI (float): The lower 95% confidence interval of the probability of losing money
        pLoseMoneyUpperCI (float): The upper 95% confidence interval of the probability of losing money
        valueAtRisk (float): The value at risk at the 5% level. Returns 0 if value at risk is positive.

    Raises:\n
        HTTPException: If the input values do not satisfy the following conditions:
            yearOneSales must fit a triangular distribution
            annualMarginDecrease must be between 0 and 1
            annualSalesDecay must be all 0 or fit a triangular distribution
            taxRate must be between 0 and 1
            discountRate must be between 0 and 1
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
            detail="Please check that annualSalesDecayMin <= annualSalesDecayMode <= annualSalesDecayMax and annualSalesDecayMin < annualSalesDecayMax. Or set annualSalesDecayMin, annualSalesDecayMode, and annualSalesDecayMax all to 0 to remove from model.",
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
    (
        mean_npv,
        mean_std_error,
        mean_lower_ci,
        mean_upper_ci,
        p_lose_money_lower_ci,
        p_lose_money_upper_ci,
        value_at_risk,
    ) = generate_stats(simulated_profits).values()

    return {
        "simulatedNPVs": simulated_profits,
        "meanNPV": mean_npv,
        "meanStandardError": mean_std_error,
        "meanLowerCI": mean_lower_ci,
        "meanUpperCI": mean_upper_ci,
        "pLoseMoneyLowerCI": p_lose_money_lower_ci,
        "pLoseMoneyUpperCI": p_lose_money_upper_ci,
        "valueAtRisk": value_at_risk,
    }


# @desc Monte Carlo simulation for cash flow
# @route GET /api/simulations/cash_flow
# @access public
@router.get("/cash_flow")
def simulation_cash_flow(
    periodsPerYear: int,
    fixedCost: float,
    min: float,
    mean: float,
    max: float,
    sd: float,
):
    """
    Monte Carlo simulation for annual cash flow. The arguments provided determine the distribution of periodic cash flows. Periodic cash flow can follow a triangular, truncated normal, uniform, or normal distribution.\n

    Args:\n
        periodsPerYear (int): The number of periods per year.\n
        fixedCost (float): The total annual fixed costs.\n
        min (float): The minimum periodic cash flow.\n
        mean (float): The mean periodic cash flow.\n
        max (float): The maximum periodic cash flow.\n
        sd (float): The standard deviation of periodic cash flows.\n

    Returns:\n
        annualCashFlows (list): A list of annualized cash flows.\n

    Raises:\n
        HTTPException: If the input values do not satisfy the following conditions:

            periodsPerYear > 0

            triangular distribution:
                min <= mean <= max
                min < max
                sd = 0

            normal distribution:
                min = 0
                max = 0
                sd > 0

            truncated normal distribution:
                min <= mean <= max
                min < max
                sd > 0

            uniform distribution:
                min < max
                mean = 0
                sd = 0
            A 400 status code and an error message are returned in this case.

    """
    # validate data
    if periodsPerYear <= 0:
        raise HTTPException(
            status_code=400,
            detail="periodsPerYear must be greater than 0.",
        )
    # set seed
    rng = np.random.default_rng(seed=42)

    # define truncated normal function
    def truncated_normal(min: float, mean: float, max: float, sd: float) -> float:
        value = rng.normal(mean, sd)
        if value < min or value > max:
            value = truncated_normal(min, max, mean, sd)
        return value

    # determine distribution
    # triangular
    if is_triangular(min, mean, max) and sd == 0:
        distribution = rng.triangular(min, mean, max, 1000).tolist()
    # truncated normal
    elif is_triangular(min, mean, max) and sd > 0:
        distribution = [truncated_normal(min, mean, max, sd) for _ in range(0, 1000)]
    # uniform
    elif mean == 0 and sd == 0 and min < max:
        distribution = rng.uniform(min, max, 1000).tolist()
    # normal
    elif min == 0 and max == 0 and sd > 0:
        distribution = rng.normal(mean, sd, 1000).tolist()
    # else raise exception
    else:
        raise HTTPException(
            status_code=400,
            detail="Cash flows must follow one of the following distributions: triangular, truncated normal, uniform, or normal.",
        )

    # define simulation
    def simulation():
        return rng.choice(distribution, periodsPerYear).sum() - fixedCost

    # run simulation
    annual_cash_flows = [simulation() for _ in range(1000)]

    return {"annualCashFlows": annual_cash_flows}
