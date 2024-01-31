from typing import List, Optional

from ..actions import Action
from . import LLM, Message


class Session:
    def __init__(self, llm: LLM, actions: Optional[List[Action]] = None) -> None:
        self._llm = llm
        self._actions = actions
        self._messages = []

    def add(self, message: Message):
        self._messages.append(message)

    @property
    def messages(self) -> List[Message]:
        return self._messages

    def run(self):
        m = self._llm.chat(messages=self._messages[-5:], functions=self._actions)
        if m.observations is not None:
            for om in m.observations:
                om.role = "assistant"
                self.add(om)
        self.add(m)
        return m
