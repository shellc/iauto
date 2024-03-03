import streamlit as st

from iauto.playground import utils

st.set_page_config(
    page_title='iauto Playground',
    page_icon='🦾',
    layout='wide',
    initial_sidebar_state="expanded"
)

utils.logo()

st.title("ia")
