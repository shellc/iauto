from typing import List
import json
from ._llm import LLM, Message
from ..actions import Action
import chatglm_cpp


class ChatGLM(LLM):
    def __init__(self, model_path) -> None:
        super().__init__()
        self._llm = chatglm_cpp.Pipeline(model_path=model_path)

    def generate(self, instructions: str, functions: List[Action] = None, **kwargs) -> Message:
        """"""
        messages = []
        messages.append(Message(
            role="user",
            content=instructions
        ))

        return self.chat(messages=messages, functions=functions, **kwargs)

    def chat(self, messages: List[Message] = [], functions: List[Action] = None, **kwargs) -> Message:
        if functions is not None:
            function_descriptions = [f.definition().openai_function() for f in functions]
            system_instructions = """
                Answer the following questions as best as you can. You have access to the following tools:\n
            """
            system_instructions += json.dumps(function_descriptions, ensure_ascii=False, indent=4)

            messages.insert(-1, Message(
                role="system",
                content=system_instructions
            ))

        chatglm_messages = []
        for m in messages:
            chatglm_messages.append(chatglm_cpp.ChatMessage(role=m.role, content=m.content))
        r = self._llm.chat(messages=chatglm_messages)

        tool_calls = r.tool_calls

        r_content = None
        if tool_calls and functions:
            resp = []

            available_function = dict(
                [(func.definition().name, func) for func in functions]
            )

            def tool_call(**kwargs):
                return kwargs

            for tc in tool_calls:
                func_name = tc.function.name
                if not func_name:
                    continue
                func_to_call = available_function[func_name]

                func_resp = None
                try:
                    func_args = eval(tc.function.arguments, dict(tool_call=tool_call))
                    func_resp = func_to_call(**func_args)
                except Exception as e:
                    func_resp = str(e)
                if not isinstance(func_resp, str):
                    func_resp = json.dumps(func_resp or {}, ensure_ascii=False, indent=4)
                resp.append(func_resp)

            r_content = '\n'.join(resp) if len(resp) > 0 else "."
        else:
            r_content = r.content

        return Message(role="assistant", content=r_content)
