"""general utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import List, Tuple, TypeVar

T = TypeVar('T')


def is_even(number: int) -> bool:
    return (number % 2) == 0


def sorted_tuple(files: List[T]) -> Tuple[T, ...]:
    return tuple(sorted(set(files)))
