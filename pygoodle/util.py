"""general utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from typing import Callable, Iterable, Optional, Tuple, TypeVar

T = TypeVar('T')


def is_even(number: int) -> bool:
    return (number % 2) == 0


def sorted_tuple(items: Iterable[T], unique: bool = False, reverse: bool = False,
                 key: Optional[Callable] = None) -> Tuple[T, ...]:
    if unique:
        items = set(items)
    return tuple(sorted(items, reverse=reverse, key=key))
