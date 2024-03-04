import glob
import os

import streamlit as st

import iauto


def list_actions():
    actions = [a.spec for a in iauto.actions.loader.actions]
    actions.sort(key=lambda x: x.name)
    return actions


def list_playbooks():
    playbooks = {}

    playbooks_dir = os.environ["IA_PLAYBOOK_DIR"]

    if playbooks_dir and os.path.isdir(playbooks_dir):
        files = glob.glob("**/*.y*ml", root_dir=playbooks_dir, recursive=True)
        files = [f for f in files if f.endswith((".yml", ".yaml"))]
        for name in files:
            f = os.path.join(playbooks_dir, name)
            if not os.path.isfile(f):
                continue
            try:
                playbbook = iauto.load(f)
            except Exception:
                continue

            playbbook_desc = name.replace(".yaml", "").replace(".yml", "")
            if playbbook.description:
                playbbook_desc = playbbook.description
            elif playbbook.spec and playbbook.spec.description:
                playbbook_desc = playbbook.spec.description

            playbooks[(f, playbbook_desc)] = playbbook

    return playbooks


def logo():
    pass


def _logo():
    st.markdown(
        """
            <style>
                [data-testid="stSidebar"] {{
                    background-image: url(app/static/ia.png);
                    background-repeat: no-repeat;
                    padding-top: 0px;
                    background-position: 20px 15px;
                    background-size: 64px;
                }}
                [data-testid="stSidebar"]::before {{
                    content: "ia";
                    margin-left: 90px;
                    margin-top: 36px;
                    font-size: 18px;
                    position: absolute;
                    top: 0px;
                }}
            </style>
            """,
        unsafe_allow_html=True,
    )
