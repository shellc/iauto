from typing import Any, List, Optional, Union

from ..actions import Action, ActionSpec, Executor, Playbook, loader
from .llm import ChatMessage
from .llm_factory import create_llm
from .session import Session


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
        provider="openai",
        llm_args={},
        tools: Optional[List[str]] = None,
        executor: Executor,
        playbook: Playbook,
        **kwargs
    ) -> Session:
        if executor is None or playbook is None:
            raise ValueError("executor and playbook required.")

        llm = create_llm(provider=provider, **llm_args)

        actions = []

        if tools is not None:
            for name in tools:
                action = loader.get(name)
                if action is None:
                    raise ValueError(f"Action not found: {name}")
                actions.append(action)

        if playbook.actions is not None:
            for action_pb in playbook.actions:
                action = executor.get_action(playbook=action_pb)
                if action is None:
                    raise ValueError(f"Action not found: {action_pb.name}")
                if action_pb.name == "playbook":
                    args_, kwargs_ = executor.eval_args(args=action_pb.args)
                    pb_run_actions = action.perform(
                        *args_, execute=False, executor=executor, playbook=action_pb, **kwargs_)
                    actions.extend(pb_run_actions)
                else:
                    raise ValueError(f"Actions must be playbook, invalid action: {action_pb.name}")

        session = Session(llm=llm, actions=actions)
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
        if isinstance(m, dict) or isinstance(m, list):
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
