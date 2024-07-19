# utility functions for validation
def is_triangular(min: float, mode: float, max: float):
    return min <= mode and mode <= max and min < max


def is_percent(num: float):
    return num >= 0 and num <= 1


def is_all_zero(*args):
    return all(value == 0 for value in args)
