import glob
import os

import iauto


def list_actions():
    actions = [a.spec for a in iauto.actions.loader.actions]
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

            playbooks[(playbbook_desc, f)] = playbbook
    return playbooks
