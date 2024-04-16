
import unittest

from iauto.actions import playbook


class TestPlaybookLoading(unittest.TestCase):
    def test_playbook_loading(self):
        playbook.load("./tests/data/playbooks/playbook_load_test.yaml")
        # playbook.dump(pb, "./tests/data/playbooks/playbook_load_test_dump.yaml", format="yaml")
        playbook.load("./tests/data/playbooks/playbook_load_test.json")
        # playbook.dump(pb, "./tests/data/playbooks/playbook_load_test_dump.json", format="json")
