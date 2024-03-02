import streamlit as st
from dotenv import dotenv_values

st.set_page_config(
    page_title='Settings',
    page_icon='⚙️',
    layout='centered',
    initial_sidebar_state="expanded"
)

st.title("Settings")

env = dotenv_values()
env
