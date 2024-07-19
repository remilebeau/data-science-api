from fastapi import APIRouter
from ..controllers.distributions import (
    distribution_triangular,
    distribution_uniform,
    distribution_truncated_normal,
    distribution_bootstrap,
)


router = APIRouter(
    prefix="/api/distributions",
    tags=["Distributions"],
    responses={404: {"description": "Not found"}},
)


@router.get("/triangular")
def route():
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
    distribution_triangular()


@router.get("/uniform")
def route():
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
    distribution_uniform()


@router.get("/truncated_normal")
def route():
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
    distribution_truncated_normal()


@router.post("/bootstrap")
def route():
    distribution_bootstrap()
