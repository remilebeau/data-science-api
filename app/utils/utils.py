import numpy as np


def is_triangular(min: float, mode: float, max: float, sd: float):
    return (min <= mode <= max) and (min < max) and (sd == 0)


def is_truncated_normal(min: float, mean: float, max: float, sd: float):
    return (min <= mean <= max) and (min < max) and (sd > 0)


def generate_stats(values: list[float]):
    minimum = np.min(values)
    value_at_risk = min(np.percentile(values, 5), 0)
    q1 = np.percentile(values, 25)
    median = np.percentile(values, 50)
    q3 = np.percentile(values, 75)
    maximum = np.max(values)
    mean_profit = np.mean(values)
    mean_profit_lower_ci = mean_profit - 1.96 * np.std(values) / np.sqrt(len(values))
    mean_profit_upper_ci = mean_profit + 1.96 * np.std(values) / np.sqrt(len(values))
    p_lose_money = sum(profit < 0 for profit in values) / len(values)
    p_lose_money_lower_ci = p_lose_money - 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / len(values)
    )
    p_lose_money_upper_ci = p_lose_money + 1.96 * np.sqrt(
        p_lose_money * (1 - p_lose_money) / len(values)
    )
    return (
        minimum,
        value_at_risk,
        q1,
        median,
        q3,
        maximum,
        mean_profit,
        mean_profit_lower_ci,
        mean_profit_upper_ci,
        p_lose_money,
        p_lose_money_lower_ci,
        p_lose_money_upper_ci,
    )
