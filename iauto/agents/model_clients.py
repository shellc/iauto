import json
from types import SimpleNamespace
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

from autogen import ModelClient

from iauto.llms import ChatMessage, Session

from .. import log


class SessionResponse(SimpleNamespace):
    class Choice(SimpleNamespace):
        class Message(SimpleNamespace, Iterable):
            role: Optional[str]
            content: Optional[str]
            tool_calls: Optional[List[Dict]]

            def __iter__(self) -> Iterator[Tuple]:
                return iter([
                    ("role", self.role),
                    ("content", self.content),
                    ("tool_calls", self.tool_calls)
                ])

            def __getitem__(self, index):
                d = dict(self)
                return d.get(index)

        message: Message

    choices: List[Choice]
    model: str
    usage: Dict[str, int]


class SessionClient(ModelClient):
    def __init__(
        self,
        config,
        session: Session,
        react: Optional[bool] = False,
        llm_args: Optional[Dict] = None,
        **kwargs
    ) -> None:
        self._model = config.get("model")
        self._session = session
        self._react = react
        self._llm_args = llm_args or {}

        self._log = log.get_logger("IASessionClient")

    def create(self, params: Dict[str, Any]) -> ModelClient.ModelClientResponseProtocol:
        if self._log.isEnabledFor(log.DEBUG):
            self._log.debug(json.dumps(params, indent=4, ensure_ascii=False))

        messages = []

        for m in params.get("messages") or []:
            messages.append(ChatMessage(
                role=m["role"],
                content=m["content"] or "",
                tool_call_id=m.get("tool_call_id"),
                name=m.get("name"),
                tool_calls=m.get("tool_calls")
            ))

        tool_calls = params.get("tools") or []
        use_tools = len(tool_calls) > 0

        if self._react:
            m = self._session.react(messages=messages, use_tools=use_tools, auto_exec_tools=False, **self._llm_args)
        else:
            m = self._session.run(messages=messages, use_tools=use_tools, auto_exec_tools=False, **self._llm_args)

        if not isinstance(m, ChatMessage):
            raise ValueError("invalid message type response from SessionClient")

        # if self._log.isEnabledFor(log.DEBUG):
        #    self._log.debug(json.dumps(m.model_dump(), indent=4, ensure_ascii=False))

        usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        if m.usage:
            usage["prompt_tokens"] = m.usage.input_tokens
            usage["completion_tokens"] = m.usage.output_tokens

        resp = SessionResponse(
            choices=[
                SessionResponse.Choice(
                    message=SessionResponse.Choice.Message(
                        role=m.role,
                        content=m.content,
                        tool_calls=[t.model_dump() for t in m.tool_calls or []]
                    )
                )
            ],
            model=self._model,
            usage=usage
        )

        return resp

    def message_retrieval(
        self,
        response: ModelClient.ModelClientResponseProtocol
    ) -> Union[List[str], List[ModelClient.ModelClientResponseProtocol.Choice.Message]]:
        choices = response.choices

        has_tool_calls = False
        for choice in choices:
            tool_calls = choice.message["tool_calls"]
            if tool_calls and len(tool_calls) > 0:
                has_tool_calls = True
                break

        if has_tool_calls:
            return [c.message for c in choices]
        else:
            return [c.message["content"] for c in choices if c.message["content"] is not None]

    def cost(self, response: SessionResponse) -> float:
        return 0

    @staticmethod
    def get_usage(response: SessionResponse) -> Dict:
        usage = response.usage
        usage["cost"] = 0
        usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
        return usage
