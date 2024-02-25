from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel

from ..actions import ActionSpec


class Function(BaseModel):
    name: str
    arguments: Optional[str] = None


class ToolCall(BaseModel):
    id: str
    type: str
    function: Optional[Function] = None


class Message(BaseModel):
    content: str


class ChatMessage(Message):
    role: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    @staticmethod
    def from_dict(d: Dict) -> "ChatMessage":
        m = ChatMessage(role="", content="")
        m.role = d.get("role") or ""
        m.content = d.get("content") or ""
        m.tool_call_id = d.get("tool_call_id")
        m.name = d.get("name")

        m.tool_calls = []
        tool_calls = d.get("tool_calls") or []
        for tool_call in tool_calls:
            m.tool_calls.append(
                ToolCall(
                    id=tool_call["id"],
                    type=tool_call["type"],
                    function=Function(
                        name=tool_call["function"]["name"],
                        arguments=tool_call["function"]["arguments"]
                    )
                )
            )
        return m


class LLM(ABC):
    """LLM"""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(self, instructions: str, **kwargs) -> Message:
        """"""

    @abstractmethod
    def chat(self, messages: List[ChatMessage], tools: Optional[List[ActionSpec]] = None, **kwargs) -> ChatMessage:
        """"""

    @property
    def model(self) -> str:
        ...
