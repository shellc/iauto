import streamlit as st

st.set_page_config(
    page_title='iauto Playground',
    page_icon='🦾',
    layout='wide',
    initial_sidebar_state="expanded"
)

st.markdown("""
<div style="text-align: center">
<img src="https://shellc.cn/iauto/assets/img/icon.svg" width="120" style="filter: invert(50%)" />
</div>
""", unsafe_allow_html=True)

st.title("iauto")
