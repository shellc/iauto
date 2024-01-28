from typing import List

from ..actions import Action
from . import LLM, Message


class Session:
    def __init__(self, llm: LLM, actions: List[Action] = None) -> None:
        self._llm = llm
        self._actions = actions
        self._messages = []

    def add(self, message: Message):
        self._messages.append(message)

    @property
    def messages(self) -> List[Message]:
        return self._messages

    def run(self):
        m = self._llm.chat(messages=self._messages, functions=self._actions)
        self.add(m)
        return m
