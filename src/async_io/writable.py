from typing import Generic, TypeVar
from abc import ABC, abstractmethod


T = TypeVar('T')


class Writable(Generic[T], ABC):

    @abstractmethod
    async def write(self, source: T) -> int:
        ...
