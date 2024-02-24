import os

import streamlit as st

from iauto import PlaybookExecutor
from iauto.agents import AgentExecutor
from iauto.llms import ChatMessage, Session

# here = os.path.dirname(__file__)
# playbooks_dir = os.path.abspath(os.path.join(here, os.path.pardir, "playbooks"))
playbooks_dir = os.environ["IA_PLAYBOOK_DIR"]

st.set_page_config(
    page_title='Agents',
    page_icon='🤖',
    layout='wide'
)

# Initialize agent


def print_received(message, sender, receiver):
    avatar = "🤖"
    with st.chat_message(sender.name, avatar=avatar):
        content = message if isinstance(message, str) else message["content"]
        content = f"**{sender.name}** -> **{receiver.name}**\n\n{content}"
        st.markdown(content)
        st.session_state.messages.append({"role": sender.name, "content": content, "avatar": avatar})


def create_llm(llm_mode, playbook_vars):
    if llm_mode == "Chat" or llm_mode == "ReAct":
        return PlaybookExecutor.execute(os.path.join(playbooks_dir, "llm_chat.yaml"), variables=playbook_vars)
    elif llm_mode == "Multi-Agent":
        agent = PlaybookExecutor.execute(os.path.join(playbooks_dir, "agents.yaml"), variables=playbook_vars)

        agent.register_print_received(print_received)
        agent.set_human_input_mode("NEVER")

        return agent


def reset(llm):
    if isinstance(llm, Session):
        llm.messages.clear()
    elif isinstance(llm, AgentExecutor):
        llm.reset()
    st.session_state.messages.clear()


# Sidebar
playbook_vars = {
    "llm_provider": "openai",
    "llm_args": {},
    "llm_chat_args": {}
}
st.session_state["llm_args"] = {}
st.session_state["llm_chat_args"] = {}

with st.sidebar:
    llm_mode = st.radio(
        "Mode",
        ["Chat", "ReAct", "Multi-Agent"]
    )

    llm_provider = st.radio(
        "Provider",
        ["OpenAI", "LLaMA", "ChatGLM"],
        captions=["OpenAI compatible API", "llama.cpp GGUF models", "chatglm.cpp GGUF model"]
    )

    if llm_provider == "OpenAI":
        playbook_vars["llm_provider"] = "openai"
        api_key = st.text_input(
            "API Key",
            value=st.session_state["llm_args"].get("api_key", os.environ.get("OPENAI_API_KEY") or "sk-")
        )
        playbook_vars["llm_args"]["api_key"] = api_key
        st.session_state["llm_args"]["api_key"] = api_key

        base_url = st.text_input(
            "API Base URL",
            value=st.session_state["llm_args"].get("base_url", os.environ.get("OPENAI_API_BASE") or None)
        )
        playbook_vars["llm_args"]["base_url"] = base_url
        st.session_state["llm_args"]["base_url"] = base_url

        model = st.text_input(
            "Model",
            value=st.session_state["llm_args"].get("model",  os.environ.get("OPENAI_MODEL_NAME") or "gpt-3.5-turbo")
        )
        playbook_vars["llm_args"]["model"] = model
        st.session_state["llm_args"]["model"] = model
    elif llm_provider == "LLaMA":
        playbook_vars["llm_provider"] = "llama"

        model = st.text_input("Model path", value=st.session_state["llm_args"].get(
            "llama_model_path", "/Volumes/Workspaces/models/Qwen-1_8B-Chat/ggml-model-q4_0.gguf"))
        playbook_vars["llm_args"]["model_path"] = model
        st.session_state["llm_args"]["llama_model_path"] = model

        chat_format = st.text_input("Chat format", value=st.session_state["llm_args"].get("chat_format", "qwen-fn"))
        playbook_vars["llm_args"]["chat_format"] = chat_format
        st.session_state["llm_args"]["chat_format"] = chat_format

        repeat_penalty = st.number_input(
            "repeat_penalty", value=st.session_state["llm_chat_args"].get("repeat_penalty", 1.2))
        playbook_vars["llm_chat_args"]["repeat_penalty"] = repeat_penalty
        st.session_state["llm_chat_args"]["repeat_penalty"] = repeat_penalty
    elif llm_provider == "ChatGLM":
        playbook_vars["llm_provider"] = "chatglm"

        model = st.text_input("Model path", value=st.session_state["llm_args"].get(
            "chatglm_model_path", "/Volumes/Workspaces/models/chatglm3-6b/chatglm3-6b-ggml.bin"))
        playbook_vars["llm_args"]["model_path"] = model
        st.session_state["llm_args"]["chatglm_model_path"] = model

    if llm_provider != "OpenAI":
        top_k = st.number_input("top_k", value=st.session_state["llm_chat_args"].get("top_k", 2))
        playbook_vars["llm_chat_args"]["top_k"] = top_k
        st.session_state["llm_chat_args"]["top_k"] = top_k

    temperature = st.number_input("temperature", value=st.session_state["llm_chat_args"].get("temperature", 0.75))
    playbook_vars["llm_chat_args"]["temperature"] = temperature
    st.session_state["llm_chat_args"]["temperature"] = temperature

    use_tools = st.checkbox("Use tools", value=False)

    label = "Reload" if st.session_state.get("llm") else "Launch"
    if st.button(label=label, type="primary"):
        st.session_state.llm = create_llm(llm_mode=llm_mode, playbook_vars=playbook_vars)

# Main container
if st.session_state.get("llm"):
    st.markdown(f"#### {llm_provider} {llm_mode}")

if st.session_state.get("llm") and len(st.session_state.messages) == 0:
    greeting = "Hello! How can I help you today?"
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    with st.chat_message(role, avatar=message.get("avatar")):
        if message["role"] == "user":
            content = f"{content}"
        st.markdown(content)

if st.session_state.get("llm") is not None:
    llm = st.session_state.llm

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(f"{prompt}")

        # Display assistant response in chat message container
        resp_message = None
        if llm_mode == "Chat" or llm_mode == "ReAct":
            llm.add(ChatMessage(role="user", content=prompt))
            if llm_mode == "Chat":
                resp = llm.run(**playbook_vars["llm_chat_args"], use_tools=use_tools)
            elif llm_mode == "ReAct":
                resp = llm.react(**playbook_vars["llm_chat_args"], use_tools=use_tools)
            resp_message = resp.content
        elif llm_mode == "Multi-Agent":
            resp = llm.run(message=ChatMessage(role="user", content=prompt), clear_history=False)
            resp_message = resp["summary"]
        else:
            raise ValueError(f"Invalid llm: {type(llm)}")

        with st.chat_message("assistant"):
            st.markdown(resp_message)
            st.session_state.messages.append({"role": "assistant", "content": resp_message})

    if len(st.session_state.messages) > 1:
        st.button("Clear", type="secondary", help="Clear history", on_click=lambda: reset(llm))
