import os

import streamlit as st

import iauto
from iauto.llms import ChatMessage
from iauto.playground import llm_options, utils

st.set_page_config(
    page_title='Agent',
    page_icon='🤖',
    layout='wide'
)

utils.logo()

here = os.path.dirname(__file__)
playbooks_dir = os.path.abspath(os.path.join(here, os.path.pardir, "playbooks"))

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_actions" not in st.session_state:
    st.session_state.tool_actions = set()
if "tool_playbooks" not in st.session_state:
    st.session_state.tool_playbooks = set()

messages = st.session_state.messages
tool_actions = st.session_state.tool_actions
tool_playbooks = st.session_state.tool_playbooks

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


def create_llm(llm_mode, args):
    args["tools"] = list(tool_actions)
    args["playbooks"] = list(tool_playbooks)

    agent_executor = iauto.execute(os.path.join(playbooks_dir, "agents.yaml"), variables=args)
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
config = {
    "llm_provider": "openai",
    "llm_args": {},
    "llm_chat_args": {},
    "react": False
}

with st.sidebar:
    llm_mode = st.radio(
        "Mode",
        ["Chat", "ReAct", "Multi-Agent"]
    )

    if llm_mode == "Multi-Agent":
        config["react"] = st.checkbox("Enable agents ReAct", value=False)

    options = llm_options.render()
    config.update(options)

    use_tools = st.checkbox("Use tools", value=False)

    # Tools
    if use_tools:
        actions = utils.list_actions()
        playbooks = utils.list_playbooks()
        with st.expander("Tools"):
            for desc, file in playbooks.keys():
                if st.checkbox(desc):
                    tool_playbooks.add(file)
                else:
                    tool_playbooks.discard(file)
            for action in actions:
                if st.checkbox(action.name, help=action.description):
                    tool_actions.add(action.name)
                else:
                    tool_actions.discard(action.name)

    label = "Reload" if agent_executor else "Launch"
    if st.button(label=label, type="primary"):
        reset()
        create_llm(llm_mode=llm_mode, args=config)
        st.rerun()

# Main container
if agent_executor:
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

        resp_message = None
        if llm_mode == "Chat":
            with st.spinner("Generating..."):
                resp = agent_executor.session.run(**config["llm_chat_args"], use_tools=use_tools)
                resp_message = resp.content
        elif llm_mode == "ReAct":
            with st.spinner("Reacting..."):
                resp = agent_executor.session.react(**config["llm_chat_args"], use_tools=use_tools)
                resp_message = resp.content
        elif llm_mode == "Multi-Agent":
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
