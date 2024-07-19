import numpy as np
import numpy_financial as npf
from fastapi import HTTPException
from ..utils import is_triangular, is_percent, is_all_zero


# @desc Monte Carlo simulation for production planning. Triangular distribution. n = 1000. α = 0.05
# @route GET /api/simulations/production
# @access public
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
