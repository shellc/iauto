from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from ia.llms import create_llm, Message
from ia.actions import load_actions
from ia._session import Session

llm_args = {
    "model_path": "/Users/shellc/Workspaces/chatglm.cpp/chatglm-ggml.bin"
}

actions = load_actions([
    "ia.actions.system.execute_command.ExecuteCommand"
])

llm = create_llm(provider="chatglm", **llm_args)
session = Session(llm=llm, actions=actions)

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
