from utils import general

import subprocess
import unittest

class test_get_cmd_content_limit(unittest.TestCase):
    def test_within_and_over_limit(self):
        payload_limit, meta_limit = general.get_cmd_content_limit()
        base_cmd = ["python", "-c", "import sys; print(len(sys.argv[1]))"]

        payload_ok = "A" * payload_limit
        cmd_ok = base_cmd + [payload_ok]
        try:
            subprocess.run(cmd_ok, check=True)
        except subprocess.CalledProcessError as e:
            self.fail(f"Command within limit failed unexpectedly: {e}")

        payload_nok = payload_ok + "B" * meta_limit
        cmd_nok = base_cmd + [payload_nok]
        with self.assertRaises((OSError, subprocess.CalledProcessError)):
            subprocess.run(cmd_nok, check=True)

if __name__ == "__main__":
    unittest.main()
