from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from ia.llms import create_llm
from ia.tools import load_functions

llm_args = {
    
    "model_path": "/Users/shellc/Workspaces/chatglm.cpp/chatglm-ggml.bin"
}
llm_model = "Qwen-14B-Chat-Int4"
# llm_model = "gpt-3.5-turbo"


llm = create_llm(provider="chatglm", **llm_args)

functions = load_functions([
    #"ia.tools.system.fs.Ls",
    "ia.tools.system.cmd.Command"
])

try:
    history = InMemoryHistory()
    while True:
        instructions = prompt("Human: ", history=history, auto_suggest=AutoSuggestFromHistory())
        r = llm.generate(
            instructions,
            model=llm_model,
            functions=functions
        )
        print("AI:", r)
except KeyboardInterrupt:
    print("\nBye.")
