import os
from typing import Any, List, Optional, Union

from ..actions import (Action, ActionSpec, Executor, Playbook,
                       PlaybookRunAction, loader)
from ._llm import ChatMessage
from ._llm_factory import create_llm
from ._session import Session


class CreateSessionAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "llm.session",
            "description": "Create a session for chat with LLM.",
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        provider="openai",
        llm_args={},
        actions: Optional[List[str]] = None,
        playbooks: Optional[List[str]] = None,
        **kwargs
    ) -> Session:
        llm = create_llm(provider=provider, **llm_args)
        functions = []
        if actions is not None:
            for name in actions:
                action = loader.get(name)
                if action is None:
                    raise ValueError(f"Action not found: {name}")
                functions.append(action)

        if playbooks is not None:
            if executor is None:
                raise ValueError("executor is required.")

            root_path = executor.variables.get("__file__")
            if root_path:
                root_path = os.path.dirname(root_path)
            for pb_name in playbooks:
                if not os.path.isabs(pb_name) and root_path is not None:
                    pb_name = os.path.join(root_path, pb_name)
                    pb = Playbook.load(pb_name)

                    # def _action_func(*args, **kwargs):
                    #    for k, v in kwargs.items():
                    #        executor.set_variable(f"${k}", v)
                    #    return executor.perform(playbook=pb)
                    if pb.spec is None:
                        raise ValueError("As the function of an LLM, playbook must have spec.")
                    # action = create_action(func=_action_func, spec=pb.spec.model_dump())
                    action = PlaybookRunAction(executor=executor, playbook=pb)
                    functions.append(action)

        session = Session(llm=llm, actions=functions)
        return session


class ChatAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "llm.chat",
            "description": "Send a message to LLM and wait for a reply.",
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        session: Session,
        prompt,
        history: int = 5,
        rewrite: bool = False,
        expect_json: int = 0,
        **kwargs: Any
    ) -> Union[str, Any]:
        session.add(ChatMessage(role="user", content=prompt))
        m = session.run(history=history, rewrite=rewrite, expect_json=expect_json, **kwargs)
        if expect_json > 0:
            return m
        else:
            return m.content if m is not None else None


class ReactAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "llm.react",
            "description": "ReAct reasoning.",
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        session: Session,
        prompt,
        history: int = 5,
        rewrite: bool = False,
        log: bool = False,
        max_steps: int = 3,
        **kwargs: Any
    ) -> str:
        session.add(ChatMessage(role="user", content=prompt))
        m = session.react(history=history, rewrite=rewrite, log=log, **kwargs)
        return m.content


def register_actions():
    loader.register({
        "llm.session": CreateSessionAction(),
        "llm.chat": ChatAction(),
        "llm.react": ReactAction()
    })
