from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel

from ..actions import Action


class Message(BaseModel):
    content: str


class ChatMessage(Message):
    role: str


class LLM(ABC):
    """LLM"""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(self, instructions: str, **kwargs) -> Message:
        """"""

    @abstractmethod
    def chat(self, messages: List[ChatMessage], functions: Optional[List[Action]] = None, **kwargs) -> ChatMessage:
        """"""
