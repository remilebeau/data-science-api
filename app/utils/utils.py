def is_triangular(min: float, mode: float, max: float, sd: float):
    return (min <= mode <= max) and (min < max) and (sd == 0)


def is_truncated_normal(min: float, mean: float, max: float, sd: float):
    return (min <= mean <= max) and (min < max) and (sd > 0)
