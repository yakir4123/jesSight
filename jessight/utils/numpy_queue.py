from typing import Any, Union

import numpy as np


class NumpyQueue:
    def __init__(self, size: int) -> None:
        self._arr = np.ones(size * 2) * np.nan
        self._head = 0
        self._size = size

    @property
    def values(self) -> np.ndarray:
        tail = max(0, self._head - self._size)
        return self._arr[tail : self._head]

    def __getitem__(self, index: Union[int, slice]) -> Any:
        tail = self._head - self._size
        if tail < 0:
            tail = 0
        if isinstance(index, slice):
            assert (
                index.start * index.stop >= 0
            ), "slicing works for only the same sign."  # make sure the sign is the same
            if index.start > 0:
                arr = self._arr[tail + index.start : tail + index.stop : index.step]
            else:
                arr = self._arr[
                    self._head + index.start : self._head + index.stop : index.step
                ]
            return arr
        elif isinstance(index, int):
            if index < 0:
                return self._arr[self._head + index]
            else:
                return self._arr[tail + index]
        else:
            raise IndexError(
                "only integers, slices (`:`) are valid, if there something that numpy support and Array isn'nt than "
                "implement it!"
            )

    def push(self, item: Any) -> None:
        if self._head == len(self._arr):
            self._arr[: self._size] = self._arr[-self._size :]
            self._head = self._size

        self._arr[self._head] = item
        self._head += 1
