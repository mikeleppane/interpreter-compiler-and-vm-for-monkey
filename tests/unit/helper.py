from itertools import chain


def flatten(to_be_flatten: list[list[int]]) -> list[int]:
    return list(chain.from_iterable(to_be_flatten))
