import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class SimulationInputs(BaseModel):
    productionQuantity: float
    unitCost: float
    unitPrice: float
    salvagePrice: float
    fixedCost: float
    worstLikelyDemand: float
    expectedDemand: float
    bestLikelyDemand: float
    demandStandardDeviation: float


router = APIRouter(
    prefix="/api/simulations",
    tags=["simulations"],
)


# @DESC Monte Carlo simulation for production planning
# @ROUTE POST /api/simulations/production
# @ACCESS public
@router.post(
    "/production",
    summary="Run Monte Carlo production simulation",
    response_description="Simulation results including expected profit and risk metrics",
)
def simulation_production(inputs: SimulationInputs):
    """
    Perform a Monte Carlo simulation to evaluate the profitability of a production decision under uncertain demand.

    This endpoint simulates 1,000 scenarios of uncertain demand based on a truncated normal distribution
    defined by the worst likely, expected, and best likely demand values and the demand standard deviation.
    It calculates expected profit, profit volatility, Sharpe ratio (profit-to-risk), and the 5th and 95th
    percentile outcomes of the simulated profit distribution.

    ### Request Body:
    - **productionQuantity**: (float) Units to be produced. Fixed before demand is realized.
    - **unitCost**: (float) Cost to produce a single unit.
    - **unitPrice**: (float) Sale price per unit sold.
    - **salvagePrice**: (float) Salvage value per unsold unit.
    - **fixedCost**: (float) Total fixed costs incurred regardless of production quantity.
    - **worstLikelyDemand**: (float) 5th percentile demand estimate.
    - **expectedDemand**: (float) Expected average demand.
    - **bestLikelyDemand**: (float) 95th percentile demand estimate.
    - **demandStandardDeviation**: (float) Standard deviation of demand.

    ### Responses:
    - **200 OK**: Returns calculated simulation statistics:
        - `expectedProfit`: Mean profit across simulations.
        - `volatility`: Standard deviation of simulated profits.
        - `sharpeRatio`: Expected profit divided by volatility.
        - `worstLikelyCase`: 5th percentile of simulated profits.
        - `bestLikelyCase`: 95th percentile of simulated profits.
        - `simulatedProfits`: List of individual simulated profit outcomes.

    - **400 Bad Request**: If input constraints are violated:
        - `worstLikelyDemand` must be < `expectedDemand` < `bestLikelyDemand`.
        - `demandStandardDeviation` must be > 0.
    """
    # validate
    if (
        inputs.worstLikelyDemand >= inputs.expectedDemand
        or inputs.expectedDemand >= inputs.bestLikelyDemand
    ):
        raise HTTPException(
            status_code=400,
            detail="worstLikelyDemand must be < expectedDemand < bestLikelyDemand",
        )
    if inputs.demandStandardDeviation <= 0:
        raise HTTPException(
            status_code=400, detail="demandStandardDeviation must be > 0"
        )

    # set seed for reproducibility
    np.random.seed(42)

    def truncated_normal() -> float:
        value = np.random.normal(
            inputs.expectedDemand, inputs.demandStandardDeviation, size=1
        )[0]
        if value < inputs.worstLikelyDemand or value > inputs.bestLikelyDemand:
            value = truncated_normal()
        return value

    def simulate_production():
        # profit = salesRevenue + salvageRevenue - productionCost - fixedCost
        realizedDemand = truncated_normal()
        salesRevenue = inputs.unitPrice * min(inputs.productionQuantity, realizedDemand)
        salvageRevenue = inputs.salvagePrice * max(
            inputs.productionQuantity - realizedDemand, 0
        )
        productionCost = inputs.unitCost * inputs.productionQuantity
        fixedCost = inputs.fixedCost
        profit = salesRevenue + salvageRevenue - productionCost - fixedCost
        return profit

    simulated_profits = [simulate_production() for _ in range(1000)]
    expectedProfit = np.mean(simulated_profits)
    volatility = np.std(simulated_profits)
    sharpeRatio = expectedProfit / volatility
    worstLikelyCase = np.percentile(simulated_profits, 5)
    bestLikelyCase = np.percentile(simulated_profits, 95)
    return {
        "productionQuantity": inputs.productionQuantity,
        "unitCost": inputs.unitCost,
        "unitPrice": inputs.unitPrice,
        "salvagePrice": inputs.salvagePrice,
        "fixedCost": inputs.fixedCost,
        "worstLikelyDemand": inputs.worstLikelyDemand,
        "expectedDemand": inputs.expectedDemand,
        "bestLikelyDemand": inputs.bestLikelyDemand,
        "demandStandardDeviation": inputs.demandStandardDeviation,
        "expectedProfit": expectedProfit,
        "volatility": volatility,
        "sharpeRatio": sharpeRatio,
        "worstLikelyCase": worstLikelyCase,
        "bestLikelyCase": bestLikelyCase,
    }
