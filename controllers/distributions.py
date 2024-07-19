from fastapi import HTTPException
from pydantic import BaseModel
import numpy as np
from ..utils import is_triangular


# model for bootstrapped data
class Bootstrap(BaseModel):
    values: list[float]


# @desc returns 1000 random values from a triangular distribution
# @route GET /api/distributions/triangular
# @access public
def distribution_triangular(distMin: float, distMode: float, distMax: float):

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
def distribution_uniform(distMin: int, distMax: int):

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


# @desc return a nonparametric bootstrapped dataset
# @route POST /api/distributions/bootstrap
# @access public
def distribution_bootstrap(dataset: Bootstrap):
    values = dataset.values
    rng = np.random.default_rng(seed=42)
    bootstrap = rng.choice(values, size=len(values), replace=True).tolist()
    return {"bootstrapValues": bootstrap}


# @desc returns 1000 random values from a truncated normal distribution
# @route GET /api/distributions/truncated_normal
# @access public
def distribution_truncated_normal(
    distMin: float, distMean: float, distMax: float, distSD: float
):

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
