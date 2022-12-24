from typing import Iterable

from .utils import Attributes

def sorter(fields: Attributes, reverse:bool = False) -> list[str]:
    #evals if t1 > t2
    compare_tuples = lambda t1: '\\'.join(t1[1])

    sorted_files = sorted(fields, key=compare_tuples, reverse=reverse)

    #select files after sorting
    return [file[0] for file in sorted_files]