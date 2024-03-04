import os
import sys

import streamlit as st
from streamlit.runtime.scriptrunner import script_runner
from streamlit.web.cli import main as streamlit_main

from .. import log

env = {}


def run(app=None, playbook_dir=None):
    here = os.path.dirname(__file__)

    if app is None:
        app = "Agents"

    app_py = os.path.join(here, f"{app}.py")

    if playbook_dir is None:
        playbook_dir = str(os.getcwdb(), "UTF-8")

    os.environ["IA_PLAYBOOK_DIR"] = playbook_dir

    handle_uncaught_app_exception = script_runner.handle_uncaught_app_exception

    def exception_handler(e):
        # Custom error handling
        if os.getenv("IA_LOG_LEVEL", "INFO").lower() == "debug":
            handle_uncaught_app_exception(e)
        else:
            log.logger.warning(e)
            st.error(e)

    script_runner.handle_uncaught_app_exception = exception_handler

    sys.argv = [
        "streamlit",
        "run",
        f"{app_py}",
        "--theme.base=dark",
        "--client.showErrorDetails=False",
        "--client.toolbarMode=minimal",
        "--server.enableStaticServing=true"
    ]
    streamlit_main()
