import os
import sys

from streamlit.web.cli import main as streamlit_main


def run(app=None, playbook_dir=None):
    here = os.path.dirname(__file__)

    if app is None:
        app = "Home"

    app_py = os.path.join(here, f"{app}.py")

    if playbook_dir is None:
        playbook_dir = str(os.getcwdb(), "UTF-8")

    os.environ["IA_PLAYBOOK_DIR"] = playbook_dir

    sys.argv = [
        "streamlit",
        "run",
        f"{app_py}",
        "--theme.base=dark",
        "--client.showErrorDetails=False"
    ]
    streamlit_main()
