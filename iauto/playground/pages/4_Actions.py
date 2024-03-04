import streamlit as st

from iauto.playground import utils

st.set_page_config(
    page_title='Actions Reference',
    page_icon='🎉',
    layout='centered',
    initial_sidebar_state="expanded"
)

utils.logo()

st.title("Actions Reference")

actions = utils.list_actions()

for a in actions:
    with st.container(border=True):
        st.markdown(f"**{a.name}**")
        st.caption(a.description)
        args = [arg.dict() for arg in a.arguments] if a.arguments is not None else []
        if len(args) > 0:
            with st.expander("Arguments", expanded=False):
                st.json(args, expanded=True)
