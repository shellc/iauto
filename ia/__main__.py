from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from ia.llms import create_llm, Message
from ia.tools import load_functions
from ia._session import Session

llm_args = {
    # "api_key": "sk-",
    # "base_url": "http://100.64.0.8:8888/v1/",
    # "api_key": "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",
    # "base_url": "https://gfw.vap.cn/openai/v1",
    "model_path": "/Users/shellc/Workspaces/chatglm.cpp/chatglm-ggml.bin"
}
llm_model = "Qwen-14B-Chat-Int4"
# llm_model = "gpt-3.5-turbo"

functions = load_functions([
    "ia.tools.system.execute_command.ExecuteCommand"
])

llm = create_llm(provider="chatglm", **llm_args)
session = Session(llm=llm, functions=functions)

try:
    history = InMemoryHistory()
    while True:
        instructions = prompt("Human: ", history=history, auto_suggest=AutoSuggestFromHistory())
        session.add(Message(
            role="user",
            content=instructions
        ))

        m = session.run()
        print("AI:", m.content)
except KeyboardInterrupt:
    print("\nBye.")
