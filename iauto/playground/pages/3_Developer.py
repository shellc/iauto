import streamlit as st

from iauto import llms
from iauto.llms.llm import ChatMessage
from iauto.playground import llm_options, utils

st.set_page_config(
    page_title='Developer',
    page_icon='👨🏻‍💻',
    layout='wide'
)

utils.logo()

with st.sidebar:
    llm_options = llm_options.render()

    if st.button(label="Reload", type="primary"):
        st.session_state["llm_session"] = None

llm_session = st.session_state.get("llm_session")
if llm_session is None:
    llm = llms.create_llm(
        provider=llm_options["llm_provider"],
        **llm_options["llm_args"]
    )

    llm_session = llms.Session(llm=llm)
    st.session_state.llm_session = llm_session


if len(llm_session.messages) == 0:
    greeting = "I can help you develop a playbook. You can give me a task, and the task description should be as clear as possible."  # noqa: E501
    # llm_session.add(llms.ChatMessage(role="assistant", content=greeting))
    with st.chat_message("assistant"):
        st.markdown(greeting)

# Display chat messages from history on app rerun
for message in llm_session.messages:
    role = message.role
    content = message.content
    with st.chat_message(role):
        if role == "user":
            content = f"{content}"
        st.markdown(content)

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(f"{prompt}")

    llm_session.add(llms.ChatMessage(role="user", content=prompt))
    with st.spinner("Generating..."):
        resp = llm_session.run(**llm_options["llm_chat_args"])

    with st.chat_message("assistant"):
        content = resp.content if isinstance(resp, ChatMessage) else resp
        st.markdown(content)


def reset():
    llm_session.messages.clear()


if len(llm_session.messages) > 1:
    st.button("Clear", type="secondary", help="Clear history", on_click=reset)

model = llm_session.llm.model
st.markdown(f"```MODEL: {model}```")
