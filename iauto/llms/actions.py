from typing import Any, Dict, List, Optional

from ..actions import Action, loader
from ._llm import Message
from ._llm_factory import create_llm
from ._session import Session


class CreateSessionAction(Action):
    def perform(
        self,
        *args,
        provider="openai",
        llm_args={},
        functions: Optional[List[Action]] = None,
        **kwargs: Any
    ) -> Session:
        llm = create_llm(provider=provider, **llm_args)
        session = Session(llm=llm, actions=functions)
        return session


class ChatAction(Action):
    def perform(self, *args, session: Session, prompt, **kwargs: Any) -> str:
        session.add(Message(role="user", content=prompt))
        m = session.run()
        return m.content


def register_actions():
    loader.register({
        "llm.session": CreateSessionAction(),
        "llm.chat": ChatAction()
    })
