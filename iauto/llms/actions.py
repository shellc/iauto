from typing import Any, Dict, List, Optional, Union

from ..actions import Action, ActionSpec, Executor, Playbook, loader
from .llm import ChatMessage
from .llm_factory import create_llm
from .session import Session


class CreateSessionAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "llm.session",
            "description": "Establish a new LLM chat session.",
            "arguments": [
                {
                    "name": "provider",
                    "type": "str",
                    "description": "The name of the LLM provider.",
                    "default": "openai"
                },
                {
                    "name": "llm_args",
                    "type": "dict",
                    "description": "Arguments to initialize the LLM.",
                    "default": {}
                },
                {
                    "name": "tools",
                    "type": "List[str]",
                    "description": "Optional list of tools to include in the session for LLM function calling.",
                    "default": None
                }
            ],
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
            "description": "Initiate a conversation with an LLM by sending a message and receiving a response.",
            "arguments": [
                {
                    "name": "session",
                    "type": "Session",
                    "description": "The active LLM session to interact with.",
                    "required": True
                },
                {
                    "name": "prompt",
                    "type": "str",
                    "description": "The message to send to the LLM.",
                    "required": True
                },
                {
                    "name": "history",
                    "type": "int",
                    "description": "The number of past interactions to consider in the conversation.",
                    "default": 5
                },
                {
                    "name": "rewrite",
                    "type": "bool",
                    "description": "Whether to rewrite the prompt before sending.",
                    "default": False
                },
                {
                    "name": "expect_json",
                    "type": "int",
                    "description": "Whether to expect a JSON response from the LLM.",
                    "default": 0
                }
            ],
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        session: Session,
        prompt: Optional[str] = None,
        messages: Optional[List[Dict]] = None,
        history: int = 5,
        rewrite: bool = False,
        expect_json: int = 0,
        **kwargs: Any
    ) -> Union[str, Any]:
        chat_messages = None
        if messages is not None and len(messages) > 0:
            chat_messages = []
            for msg in messages:
                chat_messages.append(ChatMessage(
                    role=msg["role"],
                    content=msg["content"]
                ))
        elif prompt is not None:
            session.add(ChatMessage(role="user", content=prompt))
        else:
            raise ValueError("prompt or message required.")

        m = session.run(
            messages=chat_messages,
            history=history,
            rewrite=rewrite,
            expect_json=expect_json,
            **kwargs
        )
        if isinstance(m, dict) or isinstance(m, list):
            return m
        else:
            return m.content if m is not None else None


class ReactAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "llm.react",
            "description": "Perform reactive reasoning with an LLM.",
            "arguments": [
                {
                    "name": "session",
                    "type": "Session",
                    "description": "The active LLM session to interact with.",
                    "required": True
                },
                {
                    "name": "prompt",
                    "type": "str",
                    "description": "The message to send to the LLM for reactive reasoning.",
                    "required": True
                },
                {
                    "name": "history",
                    "type": "int",
                    "description": "The number of past interactions to consider in the conversation.",
                    "default": 5
                },
                {
                    "name": "rewrite",
                    "type": "bool",
                    "description": "Whether to rewrite the prompt before sending.",
                    "default": False
                },
                {
                    "name": "log",
                    "type": "bool",
                    "description": "Whether to log the reasoning process.",
                    "default": False
                },
                {
                    "name": "max_steps",
                    "type": "int",
                    "description": "The maximum number of reasoning steps to perform.",
                    "default": 3
                }
            ],
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        session: Session,
        prompt: Optional[str] = None,
        messages: Optional[List[Dict]] = None,
        history: int = 5,
        rewrite: bool = False,
        log: bool = False,
        max_steps: int = 3,
        **kwargs: Any
    ) -> str:
        chat_messages = None
        if messages is not None and len(messages) > 0:
            chat_messages = []
            for msg in messages:
                chat_messages.append(ChatMessage(
                    role=msg["role"],
                    content=msg["content"]
                ))
        elif prompt is not None:
            session.add(ChatMessage(role="user", content=prompt))
        else:
            raise ValueError("prompt or message required.")

        m = session.react(messages=chat_messages, history=history, rewrite=rewrite, log=log, **kwargs)
        return m.content


def register_actions():
    loader.register({
        "llm.session": CreateSessionAction(),
        "llm.chat": ChatAction(),
        "llm.react": ReactAction()
    })
