import os
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title='Playbooks',
    page_icon='📚',
    layout='wide'
)

here = os.path.dirname(__file__)
playbooks_dir = os.path.abspath(os.path.join(here, os.path.pardir, "playbooks"))

for p in Path(playbooks_dir).glob("**/*.yaml"):
    st.write(p.name.replace(".yaml", ""))
