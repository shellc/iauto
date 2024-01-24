from abc import ABC, abstractmethod
from typing import Any


class Function(ABC):
    @abstractmethod
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return super().__call__(*args, **kwds)

    @abstractmethod
    def description(self) -> dict:
        return {}
