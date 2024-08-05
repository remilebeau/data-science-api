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


def is_all_zero(*args):
    return all(value == 0 for value in args)


# @desc returns mean, mean standard error, 95% confidence interval for mean, 95% confidence interval for the probability of negative profit, and value at risk at the 5% level
def generate_stats(values: list[float]) -> dict[str, float]:
    mean = np.mean(values)
    standard_error = np.std(values) / np.sqrt(len(values))
    lower_ci = mean - 1.96 * standard_error
    upper_ci = mean + 1.96 * standard_error
    p_lose_money = sum(profit < 0 for profit in values) / len(values)
    p_lose_money_lower_ci = p_lose_money - 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / len(values)
    )
    p_lose_money_upper_ci = p_lose_money + 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / len(values)
    )
    value_at_risk = min(np.percentile(values, 5), 0)
    return {
        "mean": mean,
        "standard_error": standard_error,
        "lower_ci": lower_ci,
        "upper_ci": upper_ci,
        "p_lose_money_lower_ci": p_lose_money_lower_ci,
        "p_lose_money_upper_ci": p_lose_money_upper_ci,
        "value_at_risk": value_at_risk,
    }
