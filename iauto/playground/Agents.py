import os

import streamlit as st

import iauto
from iauto.llms import ChatMessage
from iauto.playground import llm_options, utils

st.set_page_config(
    page_title='Agents',
    page_icon='🦾',
    layout='wide'
)

utils.logo()

here = os.path.dirname(__file__)
playbooks_dir = os.path.abspath(os.path.join(here, "playbooks"))

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_actions" not in st.session_state:
    st.session_state.tool_actions = []
if "tool_playbooks" not in st.session_state:
    st.session_state.tool_playbooks = []

messages = st.session_state.messages

agent_executor = st.session_state.get("agent_executor")

# Initialize agent


def print_received(message, sender, receiver):
    with st.chat_message("assistant"):
        content = ""
        if isinstance(message, str):
            content = message
        else:
            content = message["content"]
            if "tool_calls" in message:
                func_name = message["tool_calls"][0]["function"]["name"]
                func_args = message["tool_calls"][0]["function"]["arguments"]
                content = content + f"\n```python\n{func_name}({func_args})\n```"

        content = f"**{sender.name}** (to {receiver.name})\n\n{content}"
        st.markdown(content)
        messages.append({"role": "assistant", "content": content})


def create_llm(options):
    reset()

    agent_executor = iauto.execute(
        playbook_file=os.path.join(playbooks_dir, "agents.yaml"),
        variables={
            "llm_provider": options["llm_provider"][1],
            "llm_args": options["llm_args"],
            "tools": options["llm_action_tools"],
            "playbooks": options["llm_playbook_tools"],
        }
    )
    agent_executor.register_print_received(print_received)
    agent_executor.set_human_input_mode("NEVER")

    st.session_state.agent_executor = agent_executor


def clear():
    if agent_executor is not None:
        agent_executor.session.messages.clear()
        agent_executor.reset()
    messages.clear()


def reset():
    clear()
    st.session_state.agent_executor = None


def get_model():
    if agent_executor is not None:
        return agent_executor.session.llm.model


# Sidebar
with st.sidebar:
    button_label = "Reload" if agent_executor else "Launch"
    options = llm_options.render(button_label=button_label, func=create_llm)

# Main container
if agent_executor:
    llm_mode = options["llm_mode"][2]
    llm_mode_key = options["llm_mode"][1]
    st.markdown(f"#### {llm_mode}")

    if len(messages) == 0:
        greeting = "Hello! How can I help you today?"
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        with st.chat_message(role):
            if message["role"] == "user":
                content = f"{content}"
            st.markdown(content)

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"{prompt}")

        agent_executor.session.add(ChatMessage(role="user", content=prompt))

        llm_chat_args = options["llm_chat_args"]
        llm_use_tools = options["llm_use_tools"]
        resp_message = None
        if llm_mode_key == "chat":
            with st.spinner("Generating..."):
                resp = agent_executor.session.run(**llm_chat_args, use_tools=llm_use_tools)
                resp_message = resp.content
        elif llm_mode_key == "react":
            with st.spinner("Reacting..."):
                resp = agent_executor.session.react(**llm_chat_args, use_tools=llm_use_tools)
                resp_message = resp.content
        elif llm_mode_key == "agent":
            with st.status("Agents Conversation", expanded=True):
                resp = agent_executor.run(message=ChatMessage(role="user", content=prompt), clear_history=False)
                resp_message = resp["summary"]

        with st.chat_message("assistant"):
            st.markdown(resp_message)
            messages.append({"role": "assistant", "content": resp_message})

    if len(messages) > 1:
        st.button("Clear", type="secondary", help="Clear history", on_click=clear)

    model = get_model()
    st.markdown(f"```MODEL: {model}```")
else:
    st.warning("You need to launch a model first.")
