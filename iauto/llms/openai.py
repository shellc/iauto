import json
import re
from types import SimpleNamespace
from typing import List, Optional

import openai

from .. import log
from ..actions import ActionSpec
from .llm import LLM, ChatMessage, Function, Message, ToolCall, Usage


class OpenAI(LLM):
    """"""

    def __init__(self, model: Optional[str] = None, **kwargs) -> None:
        super().__init__()

        self._model = model or "gpt-3.5-turbo"

        self._openai = openai.OpenAI(**kwargs)

        self._log = log.get_logger("OpenAI")

    def generate(self, instructions: str, **kwargs) -> Message:
        if "model" not in kwargs:
            kwargs["model"] = self._model

        r = self._openai.completions.create(
            prompt=instructions,
            stream=False,
            **kwargs
        )
        return Message(content=r.choices[0].text)

    def chat(self, messages: List[ChatMessage] = [], tools: Optional[List[ActionSpec]] = None, **kwargs) -> ChatMessage:
        if "model" not in kwargs:
            kwargs["model"] = self._model

        tools_desciption = None
        tool_choice = "auto"

        if tools:
            tools_desciption = [t.oai_spec() for t in tools]

        native_tool_call = self.native_tool_call()
        use_tool_call_prompt = tools and not native_tool_call

        msgs = []

        for m in messages:
            msg = {
                "role": "user" if not native_tool_call and m.role == "tool" else m.role,
                "content": m.content
            }
            if m.tool_call_id:
                msg["tool_call_id"] = m.tool_call_id
            if m.name:
                msg["name"] = m.name
            if m.tool_calls:
                msg["tool_calls"] = [t.model_dump() for t in m.tool_calls]
            msgs.append(msg)

        if use_tool_call_prompt:
            msgs.insert(-1, {
                "role": "user",
                "content": self.tool_call_prompt(tools=tools_desciption)
            })

        if self._log.isEnabledFor(log.DEBUG):
            self._log.debug("Request: " + json.dumps({
                "messages": msgs,
                "tools": tools_desciption
            }, ensure_ascii=False, indent=4))

        if tools_desciption and not use_tool_call_prompt:
            kwargs["tools"] = tools_desciption
            kwargs["tool_choice"] = tool_choice

        r = self._openai.chat.completions.create(
            messages=msgs,
            **kwargs
        )

        if self._log.isEnabledFor(log.DEBUG):
            self._log.debug("Response: " + json.dumps(r.model_dump(), ensure_ascii=False, indent=4))

        m = r.choices[0].message

        resp = ChatMessage(role=m.role, content=m.content or "")
        if r.usage:
            resp.usage = Usage(
                input_tokens=r.usage.prompt_tokens,
                output_tokens=r.usage.completion_tokens
            )

        if use_tool_call_prompt:
            tool_call = self.parse_tool_call(m.content)
            if tool_call is not None:
                m.tool_calls = [tool_call]

        tool_calls = m.tool_calls
        if tool_calls:
            resp.tool_calls = []
            for tool_call in tool_calls or []:
                func_name = tool_call.function.name
                func_args = tool_call.function.arguments
                resp.tool_calls.append(
                    ToolCall(
                        id=tool_call.id,
                        type=tool_call.type,
                        function=Function(
                            name=func_name,
                            arguments=func_args
                        )
                    )
                )

        return resp

    @property
    def model(self) -> str:
        return self._model

    def native_tool_call(self):
        """Check if the model support fuction calling"""
        models = [
            "gpt-3.5",
            "gpt-4",
            "qwen"
        ]
        for m in models:
            if self._model.lower().startswith(m):
                return True
        return False

    def tool_call_prompt(self, tools):
        tools_texts = []
        for tool in tools:
            tools_texts.append(TOOL_DESC.format(
                name=tool["function"]["name"],
                description=tool["function"]["description"],
                parameters=json.dumps(tool["function"]["parameters"])
            ))

        tools_text = "\n".join(tools_texts)

        return FUNC_INSTRUCTION.format(tools_text=tools_text)

    def parse_tool_call(self, content):
        def _parse(s):
            ret = SimpleNamespace(
                id="dummy_function_call_id",
                type="function",
                function=SimpleNamespace(
                    name=None,
                    arguments=None
                )
            )
            try:
                j = json.loads(s)
                if "name" in j:
                    ret.function.name = j["name"]
                else:
                    return None
                if "parameters" in j and isinstance(j["parameters"], dict):
                    ret.function.arguments = json.dumps(j["parameters"], ensure_ascii=False)
                return ret
            except Exception:
                return None

        func_call = _parse(content)
        if func_call is None:
            json_blocks = re.findall('({.*})', content, re.MULTILINE | re.DOTALL)
            for b in json_blocks:
                func_call = _parse(b)
                if func_call is not None:
                    return func_call


TOOL_DESC = (
    'name: `{name}`; Description: `{description}`; Parameters: {parameters}'
)

FUNC_INSTRUCTION = """You have access to the following APIs:

{tools_text}

You need to decide whether to call an API to generate response based on the conversation.

If you choose to call an API, follow this steps:
1. Evaluate the actual parameters of the API as a JSON dict according to your needs.
2. Generate API call in the format within markdown code block without any additional Notes or Explanations.

If there is no API that match the conversation, you will skip API selection.

API call like this:

```json
{{
    "name": "<name of the selected API>",
    "parameters": <parameters for the API calling>
}}
```

If there is no API that match the conversation, you will skip API selection.
"""
