from abc import ABC, abstractmethod


class LLM(ABC):
    """LLM"""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(self, instructions: str, functions=None, **kwargs) -> str:
        """"""