import numpy as np

from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @desc returns 1000 random values from a given triangular distribution
# @route GET /api/distributions/
# @access public
@app.get("/api/distributions/")
def distribution(distMin: int, distMode: int, distMax: int):
    # check min <= mode and mode <= max and min < max
    if not (distMin <= distMode and distMode <= distMax and distMin < distMax):
        return {
            "error": "Min must be less than or equal to mode, and mode must be less than or equal to max"
        }, 400
    # generate triangular distribution of 1000 values using distMin, distMode, and distMax
    distValues = np.random.triangular(distMin, distMode, distMax, 1000).tolist()
    return {"distValues": distValues}


# @desc returns the sum of daysPerYear samples from a given triangular distribution to simulate yearly cash flow
# @route GET /api/simulations/
# @access public
@app.get("/api/simulations/")
def monte_carlo(distMin: int, distMode: int, distMax: int, simPeriodsPerYear: int):
    # check min <= mode and mode <= max and min < max
    if not (distMin <= distMode and distMode <= distMax and distMin < distMax):
        return {
            "error": "Min must be less than or equal to mode, and mode must be less than or equal to max"
        }, 400

    # generate triangular distribution of 1000 simValues using distMin, distMode, and distMax
    dist = np.random.triangular(distMin, distMode, distMax, 1000)

    #   take simPeriodsPerYear samples from the distribution and return their sum. 1000 simValues in total
    simValues = []
    for i in range(0, 1000):
        simValues.append(float(np.random.choice(dist, simPeriodsPerYear).sum()))

    # generate stats
    simMin = round(np.min(simValues))
    simMax = round(np.max(simValues))
    simMean = round(np.mean(simValues))
    simQ1 = round(np.percentile(simValues, 25).round(0))
    simQ2 = round(np.percentile(simValues, 50).round(0))
    simQ3 = round(np.percentile(simValues, 75).round(0))
    lowerCI = round(
        np.mean(simValues) - 1.96 * np.std(simValues) / np.sqrt(len(simValues))
    )
    upperCI = round(
        np.mean(simValues) + 1.96 * np.std(simValues) / np.sqrt(len(simValues))
    )

    return {
        "simValues": simValues,
        "simMin": simMin,
        "simMax": simMax,
        "simMean": simMean,
        "simQ1": simQ1,
        "simQ2": simQ2,
        "simQ3": simQ3,
        "lowerCI": lowerCI,
        "upperCI": upperCI,
    }
