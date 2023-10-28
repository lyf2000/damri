from itertools import chain as chain_
from typing import Iterable


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def chain(items_of_items: Iterable[Iterable], select_from: str) -> Iterable:
    return chain_.from_iterable(getattr(item, select_from) for item in items_of_items)


def unpack_to_one_list(list_: Iterable[Iterable]) -> list:
    return list(chain_.from_iterable(list_))
