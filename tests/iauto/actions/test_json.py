import unittest

from iauto.actions.buildin import json


class TestJson(unittest.TestCase):
    def test_json_dumps(self):
        s = json.dumps({"k": "v"})
        d = json.loads(s)

        self.assertEqual(d["k"], "v")
