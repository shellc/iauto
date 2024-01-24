import json
from ._llm import LLM
from ..tools import get_function_descriptions
import chatglm_cpp


class ChatGLM(LLM):
    def __init__(self, model_path) -> None:
        super().__init__()
        self._llm = chatglm_cpp.Pipeline(model_path=model_path)

    def generate(self, instructions: str, functions=None, **kwargs) -> str:
        messages = []

        if functions is not None:
            function_descriptions = get_function_descriptions(functions=functions)
            system_instructions = "Answer the following questions as best as you can. You have access to the following tools:\n"
            system_instructions += json.dumps(function_descriptions, ensure_ascii=False, indent=4)

            messages.append(chatglm_cpp.ChatMessage(
                role="system",
                content=system_instructions
            ))

        messages.append(chatglm_cpp.ChatMessage(
            role="user",
            content=instructions
        ))

        r = self._llm.chat(messages=messages)

        tool_calls = r.tool_calls

        if tool_calls:
            resp = []

            available_function = dict(
                [(func.description()['name'], functions[name]) for name, func in functions.items()]
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
                    print(func_args, func_resp)
                except Exception as e:
                    func_resp = str(e)
                if isinstance(func_resp, str):
                    resp.append(func_resp)
                else:
                    resp.append(json.dumps(func_resp or {}, ensure_ascii=False, indent=4))

            return '\n'.join(resp)
        else:
            return r.content
