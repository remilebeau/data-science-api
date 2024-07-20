from fastapi import APIRouter, HTTPException
import numpy as np
from pydantic import BaseModel
from ..utils.utils import is_triangular

router = APIRouter(
    prefix="/api/distributions",
    tags=["distributions"],
    responses={404: {"description": "Not found"}},
)


# model for bootstrapped data
class Bootstrap(BaseModel):
    values: list[float]


# @desc returns 1000 random values from a triangular distribution
# @route GET /api/distributions/triangular
# @access public
@router.get("/triangular")
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
            distMin <= distMode
            distMode <= distMax
            distMin < distMax
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
@router.get("/uniform")
def distribution_uniform(distMin: int, distMax: int):
    """
    Returns 1000 pseudorandom values from a uniform distribution.

    Args:\n
        distMin (int): The minimum value of the distribution.\n
        distMax (int): The maximum value of the distribution.\n

    Returns:\n
        distValues (list): A list of 1000 pseudorandom values from a uniform distribution.

    Raises:\n
        HTTPException: If the input values do not satisfy the following condition:
            distMin < distMax
            A 400 status code and an error message are returned in this case.
    """
    # set seed
    rng = np.random.default_rng(seed=42)
    # validate data
    if distMin >= distMax:
        raise HTTPException(
            status_code=400,
            detail="Please ensure the following: distMin < distMax",
        )
    # generate distribution
    distValues = rng.uniform(distMin, distMax, 1000).tolist()
    return {"distValues": distValues}


# @desc returns 1000 random values from a normal distribution
# @route GET /api/distributions/normal
# @access public
@router.get("/normal")
def distribution_normal(distMean: float, distSD: float):
    """
    Returns 1000 pseudorandom values from a normal distribution.

    Args:\n
        distMean (float): The mean value of the distribution.\n
        distSD (float): The standard deviation of the distribution.\n

    Returns:\n
        distValues (list): A list of 1000 pseudorandom values from a normal distribution.

    Raises:\n
        HTTPException: If the input values do not satisfy the following conditions:
            distSD >= 0
            A 400 status code and an error message are returned in this case.
    """
    # validate data
    if distSD < 0:
        raise HTTPException(
            status_code=400,
            detail="Please ensure the following: distSD >= 0",
        )

    # set seed
    rng = np.random.default_rng(seed=42)

    # generate distribution
    distValues = rng.normal(distMean, distSD, 1000).tolist()

    return {"distValues": distValues}


# @desc returns 1000 random values from a truncated normal distribution
# @route GET /api/distributions/truncated_normal
# @access public
@router.get("/truncated_normal")
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
            distMin <= distMean
            distMean <= distMax
            distMin < distMax
            distSD >= 0
            A 400 status code and an error message are returned in this case.
    """
    # validate data
    if not is_triangular(distMin, distMean, distMax) or distSD < 0:
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


# @desc return a nonparametric bootstrapped dataset
# @route POST /api/distributions/bootstrap
# @access public
@router.post("/bootstrap")
def distribution_bootstrap(dataset: Bootstrap):
    values = dataset.values
    rng = np.random.default_rng(seed=42)
    bootstrap = rng.choice(values, size=len(values), replace=True).tolist()
    return {"bootstrapValues": bootstrap}
