import streamlit as st

from iauto.playground import runner, utils

st.set_page_config(
    page_title='Settings',
    page_icon='⚙️',
    layout='wide',
    initial_sidebar_state="expanded"
)

utils.logo()

st.title("Settings")

st.json(runner.env)
