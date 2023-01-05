from typing import Generic, TypeVar
from abc import ABC, abstractmethod


T = TypeVar('T')


class Readable(Generic[T], ABC):

    @abstractmethod
    async def read(self, size: int = -1) -> T:
        ...
