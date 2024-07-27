import numpy as np


def is_triangular(min: float, mode: float, max: float):
    return (min <= mode <= max) and min < max


def is_percent(num: float):
    return 0 <= num <= 1


def is_all_zero(*args):
    return all(value == 0 for value in args)


# @desc returns mean, mean standard error, 95% confidence interval for mean, 95% confidence interval for the probability of negative profit, and value at risk at the 5% level
# @param values: list of profit values
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
