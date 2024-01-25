from typing import List
from .llms import LLM, Message
from .tools import Function


class Session:
    def __init__(self, llm: LLM, functions: List[Function]) -> None:
        self._llm = llm
        self._functions = functions
        self._messages = []

    def add(self, message: Message):
        self._messages.append(message)

    @property
    def messages(self) -> List[Message]:
        return self._messages

    def run(self):
        m = self._llm.chat(messages=self._messages, functions=self._functions)
        self.add(m)
        return m
