from typing import Any, Dict

from ..actions import Action, loader
from ._llm import Message
from ._llm_factory import create_llm
from ._session import Session


class CreateSessionAction(Action):
    def perform(self, *args, provider=None, llm_args={}, functions=None, **kwargs: Any) -> Dict:
        llm = create_llm(provider=provider, **llm_args)
        session = Session(llm=llm, actions=functions)
        return session


class ChatAction(Action):
    def perform(self, *args, session: Session = None, prompt=None, **kwargs: Any) -> Dict:
        session.add(Message(role="user", content=prompt))
        m = session.run()
        return m.content


def register_actions():
    loader.register({
        "llm.session": CreateSessionAction(),
        "llm.chat": ChatAction()
    })
