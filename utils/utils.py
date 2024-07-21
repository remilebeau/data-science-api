import numpy as np


# utility functions for validation
def is_triangular(min: float, mode: float, max: float):
    return (min <= mode <= max) and min < max


def is_percent(num: float):
    return 0 <= num <= 1


def is_all_zero(*args):
    return all(value == 0 for value in args)


def generate_stats(values: list[float]):
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
    return (
        mean,
        standard_error,
        lower_ci,
        upper_ci,
        p_lose_money_lower_ci,
        p_lose_money_upper_ci,
        value_at_risk,
    )
