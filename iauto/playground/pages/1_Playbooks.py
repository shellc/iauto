import glob
import os
import time

import streamlit as st

import iauto

st.set_page_config(
    page_title='Playbooks',
    page_icon='📚',
    layout='centered',
    initial_sidebar_state="expanded"
)

st.title("Playbooks")

st.session_state.runs = st.session_state.get("runs") or {}


def run_playbook(playbook, args):
    future = iauto.execute_in_thread(playbook, variables=args)
    st.session_state.runs[playbook] = future


def stop_run(playbook):
    future = st.session_state.runs.get(playbook)
    if future:
        future.cancel()
    future.result()
    st.session_state.runs[playbook] = None


def display_arguments(playbook, playbook_file):
    if playbbook.spec is None or playbook.spec.arguments is None:
        return
    args = {}
    with st.expander("Arguments", expanded=False):
        for arg in playbook.spec.arguments:
            v = st.text_input(arg.name, help=arg.description, key=f"{playbook_file}_{arg.name}")
            env_key = v.replace("$", "")
            if os.environ.get(env_key):
                v = os.environ[env_key]
            args[arg.name] = v
    return args


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

        with st.container(border=True):
            st.write(playbbook_desc)

            col1, col2 = st.columns((100, 18))
            with col1:
                # Arguments
                args = display_arguments(playbbook, f)
            with col2:
                future = st.session_state.runs.get(f)
                running = future is not None and future.running()

                if st.button("Running" if running else "Run", disabled=running, key=f):
                    if running:
                        stop_run(f)
                    else:
                        run_playbook(f, args=args)
                    st.rerun()

            # Result
            if future and future.done():
                with st.spinner("Status"):
                    with st.expander("Result", expanded=False):
                        try:
                            result = future.result()
                            st.write(result or "```Done with nothing return.```")
                        except Exception as e:
                            st.error(e)

for run in st.session_state.runs.values():
    if run and run.running():
        time.sleep(0.5)
        st.rerun()
