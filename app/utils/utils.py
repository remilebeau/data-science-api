import numpy as np


def is_triangular(min: float, mode: float, max: float, sd: float):
    return (min <= mode <= max) and (min < max) and (sd == 0)


def is_truncated_normal(min: float, mean: float, max: float, sd: float):
    return (min <= mean <= max) and (min < max) and (sd > 0)


# @desc returns summary stats for a list of floats: minimum, q1, median, q3, max, mean, pLoseMoney, valueAtRisk
def generate_stats(values: list[float]) -> dict[str, float]:
    minimum = np.min(values)
    q1 = np.percentile(values, 25)
    median = np.median(values)
    q3 = np.percentile(values, 75)
    max = np.max(values)
    mean = np.mean(values)
    p_lose_money = sum(profit < 0 for profit in values) / len(values)
    value_at_risk = min(np.percentile(values, 5), 0)
    return {
        "minimum": minimum,
        "q1": q1,
        "median": median,
        "q3": q3,
        "max": max,
        "mean": mean,
        "p_lose_money": p_lose_money,
        "value_at_risk": value_at_risk,
    }
