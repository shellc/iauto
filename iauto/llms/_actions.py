from typing import Any, Dict
from ..actions import Action, loader
from ._llm_factory import create_llm
from ._llm import Message
from ._session import Session


class CreateSessionAction(Action):
    def perform(self, provider, llm_args={}, functions=None, **args: Any) -> Dict:
        llm = create_llm(provider=provider, **llm_args)
        session = Session(llm=llm, actions=functions)
        return {"session": session}


class ChatAction(Action):
    def perform(self, session: Session, prompt, **args: Any) -> Dict:
        session.add(Message(role="user", content=prompt))
        m = session.run()
        return {"message": m.content}


def register_actions():
    loader.register({
        "llm.session": CreateSessionAction(),
        "llm.chat": ChatAction()
    })
