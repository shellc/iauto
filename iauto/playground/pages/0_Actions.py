import streamlit as st

import iauto

st.set_page_config(
    page_title='Actions',
    page_icon='🎉',
    layout='centered',
    initial_sidebar_state="expanded"
)

st.title("Actions")

actions = [a.spec for a in iauto.actions.loader.actions]

for a in actions:
    with st.container(border=True):
        st.markdown(f"**{a.name}**")
        st.caption(a.description)
        args = [arg.dict() for arg in a.arguments] if a.arguments is not None else []
        if len(args) > 0:
            st.write("Arguments: ")
            st.json(args, expanded=False)
