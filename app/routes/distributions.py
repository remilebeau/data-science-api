from fastapi import APIRouter, HTTPException
import numpy as np
from ..utils.utils import determine_distribution

router = APIRouter(
    prefix="/api/distributions",
    tags=["distributions"],
    responses={404: {"description": "Not found"}},
)


# @desc returns 1000 random values
# @route GET /api/distributions/random
# @access public
@router.get("/random")
def distribution_random(min: float = 0, mean: float = 0, max: float = 0, sd: float = 0):
    """
    Returns 1000 pseudorandom values based on the given parameters.
    The parameters must fit a triangular, normal, uniform, or truncated normal distribution.\n

    Args:\n
        min (float): The minimum value of the distribution.\n
        mean (float): The mean of the distribution.\n
        max (float): The maximum value of the distribution.\n
        sd (float): The standard deviation of the distribution.\n

    Returns:\n
        distValues (list): A list of 1000 pseudorandom values based on the given parameters.\n
        distribution (str): The distribution used to generate the values.\n

    Raises:\n
        HTTPException: If the inputs do not satisfy one of the following sets of conditions:

        triangular:
            min <= mean <= max
            min < max
            sd = 0

        normal:
            sd > 0
            min = 0
            max = 0

        truncated normal:
            min <= mean <= max
            min < max
            sd > 0

        uniform:
            min < max
            mean = 0
            sd = 0
    """
    rng = np.random.default_rng(seed=42)

    # custom function for truncated normal
    def truncated_normal(min, mean, max, sd):
        value = rng.normal(mean, sd)
        if value < min or value > max:
            value = truncated_normal(min, max, mean, sd)
        return value

    distribution = determine_distribution(min, mean, max, sd)
    if distribution == "normal":
        values = rng.normal(mean, sd, 1000).tolist()
        return {"distribution": distribution, "distValues": values}
    elif distribution == "uniform":
        values = rng.uniform(min, max, 1000).tolist()
        return {"distribution": distribution, "distValues": values}
    elif distribution == "triangular":
        values = rng.triangular(min, mean, max, 1000).tolist()
        return {"distribution": distribution, "distValues": values}
    elif distribution == "truncated normal":
        values = [truncated_normal(min, mean, max, sd) for _ in range(1000)]
        return {"distribution": distribution, "distValues": values}
    else:
        raise HTTPException(status_code=400, detail="unknown distribution")
