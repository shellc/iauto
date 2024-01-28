from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory

from . import Message, Session, create_llm


def run():
    llm_args = {
        "model_path": "/Users/shellc/Workspaces/chatglm.cpp/chatglm-ggml.bin"
    }

    llm = create_llm(provider="chatglm", **llm_args)
    session = Session(llm=llm)

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
