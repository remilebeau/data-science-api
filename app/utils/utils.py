import numpy as np


def is_triangular(min: float, mode: float, max: float, sd: float = 0):
    return (min <= mode <= max) and min < max and sd == 0


def is_normal(mean: float, sd: float, min: float = 0, max: float = 0):
    return mean and sd > 0 and min == 0 and max == 0


def is_uniform(min: float, max: float, mean: float = 0, sd: float = 0):
    return min < max and mean == 0 and sd == 0


def is_truncated_normal(min: float, mean: float, max: float, sd: float):
    return (min <= mean <= max) and min < max and sd > 0


def determine_distribution(
    min: float = 0, mean: float = 0, max: float = 0, sd: float = 0
) -> str:
    if is_triangular(min, mean, max, sd):
        return "triangular"
    elif is_normal(mean, sd, min, max):
        return "normal"
    elif is_uniform(min, max, mean, sd):
        return "uniform"
    elif is_truncated_normal(min, mean, max, sd):
        return "truncated normal"
    else:
        return "unknown"


def is_percent(num: float):
    return 0 <= num <= 1


# @desc returns mean, mean standard error, 95% confidence interval for mean, 95% confidence interval for the probability of negative profit, and value at risk at the 5% level
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
