def is_truncated_normal(min: float, mean: float, max: float, sd: float):
    return (min <= mean <= max) and (min < max) and (sd > 0)
