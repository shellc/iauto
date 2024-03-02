import os

import streamlit as st

import iauto
from iauto.agents import AgentExecutor
from iauto.llms import ChatMessage, Session
from iauto.playground import llm_options, utils

st.set_page_config(
    page_title='Agent',
    page_icon='🤖',
    layout='wide'
)

here = os.path.dirname(__file__)
playbooks_dir = os.path.abspath(os.path.join(here, os.path.pardir, "playbooks"))

st.session_state.tool_actions = st.session_state.get("tool_actions") or set()
st.session_state.tool_playbooks = st.session_state.get("tool_playbooks") or set()

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
        st.session_state.messages.append({"role": "assistant", "content": content})


def create_llm(llm_mode, playbook_vars):
    playbook_vars["tools"] = list(st.session_state.tool_actions)
    playbook_vars["playbooks"] = list(st.session_state.tool_playbooks)

    if llm_mode == "Chat" or llm_mode == "ReAct":
        return iauto.execute(os.path.join(playbooks_dir, "llm_chat.yaml"), variables=playbook_vars)
    elif llm_mode == "Multi-Agent":
        agent = iauto.execute(os.path.join(playbooks_dir, "agents.yaml"), variables=playbook_vars)

        agent.register_print_received(print_received)
        agent.set_human_input_mode("NEVER")

        return agent


def reset(llm):
    if isinstance(llm, Session):
        llm.messages.clear()
    elif isinstance(llm, AgentExecutor):
        llm.reset()
    st.session_state.messages.clear()


def reset_llm():
    st.session_state.llm = None


# Sidebar
playbook_vars = {
    "llm_provider": "openai",
    "llm_args": {},
    "llm_chat_args": {},
    "react": False
}

with st.sidebar:
    llm_mode = st.radio(
        "Mode",
        ["Chat", "ReAct", "Multi-Agent"],
        on_change=reset_llm
    )

    if llm_mode == "Multi-Agent":
        playbook_vars["react"] = st.checkbox("Enable agents ReAct", value=False)

    options = llm_options.render()
    playbook_vars.update(options)

    use_tools = st.checkbox("Use tools", value=False)

    # Tools
    if use_tools:
        actions = utils.list_actions()
        playbooks = utils.list_playbooks()
        with st.expander("Tools"):
            for desc, file in playbooks.keys():
                if st.checkbox(desc):
                    st.session_state.tool_playbooks.add(file)
                else:
                    st.session_state.tool_playbooks.discard(file)
            for action in actions:
                if st.checkbox(action.name, help=action.description):
                    st.session_state.tool_actions.add(action.name)
                else:
                    st.session_state.tool_actions.discard(action.name)

    label = "Reload" if st.session_state.get("llm") else "Launch"
    if st.button(label=label, type="primary"):
        st.session_state.llm = create_llm(llm_mode=llm_mode, playbook_vars=playbook_vars)

# Main container
if st.session_state.get("llm"):
    st.markdown(f"#### {llm_mode}")

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
    with st.chat_message(role):
        if message["role"] == "user":
            content = f"{content}"
        st.markdown(content)

llm = st.session_state.get("llm")
if llm is not None:
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
            with st.spinner("Generating..."):
                llm.add(ChatMessage(role="user", content=prompt))
                if llm_mode == "Chat":
                    resp = llm.run(**playbook_vars["llm_chat_args"], use_tools=use_tools)
                    resp_message = resp.content
                elif llm_mode == "ReAct":
                    resp = llm.react(**playbook_vars["llm_chat_args"], use_tools=use_tools)
                    resp_message = resp.content
        elif llm_mode == "Multi-Agent":
            with st.status("Agents Conversation", expanded=True):
                resp = llm.run(message=ChatMessage(role="user", content=prompt), clear_history=False)
            resp_message = resp["summary"]
        else:
            raise ValueError(f"Invalid llm: {type(llm)}")

        with st.chat_message("assistant"):
            st.markdown(resp_message)
            st.session_state.messages.append({"role": "assistant", "content": resp_message})

    if len(st.session_state.messages) > 1:
        st.button("Clear", type="secondary", help="Clear history", on_click=lambda: reset(llm))

model = None
if llm is not None:
    if hasattr(llm, "llm"):
        model = llm.llm.model
    if hasattr(llm, "session"):
        model = llm.session.llm.model
    st.markdown(f"```Model: {model}```")
else:
    st.warning("You need to launch a model first.")
