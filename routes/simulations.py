from fastapi import APIRouter
from ..controllers.simulations import simulation_production, simulation_finance

router = APIRouter(
    prefix="/api/simulations",
    tags=["Simulations"],
    responses={404: {"description": "Not found"}},
)


@router.get("/production")
def route():
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
        meanProfit (float): The expected profit.\n
        meanStandardError (float): The standard error of the expected profit.\n
        meanLowerCI (float): The lower 95% confidence interval for the expected profit.\n
        meanUpperCI (float): The upper 95% confidence interval for the expected profit.\n
        pLoseMoneyLowerCI (float): The lower 95% confidence interval for the probability of a negative profit.\n
        pLoseMoneyUpperCI (float): The upper 95% confidence interval for the probability of a negative profit.\n
        valueAtRisk (float): The value at risk at the 5% level. Returns 0 if value at risk is positive.\n

    Raises:\n
        HTTPException: If the inputs do not satisfy the following conditions:
            - demandMin <= demandMode
            - demandMode <= demandMax
            - demandMin < demandMax
            - productionQuantity > 0
            A 400 status code and an error message are returned in this case.

    """
    simulation_production()


@router.get("/finance")
def route():
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
            - yearOneSales must fit a triangular distribution
            - annualMarginDecrease must be between 0 and 1
            - annualSalesDecay must be all 0 or fit a triangular distribution
            - taxRate must be between 0 and 1
            - discountRate must be between 0 and 1
            A 400 status code and an error message are returned in this case.
    """
    simulation_finance()
