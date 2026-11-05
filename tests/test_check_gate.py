"""Tests for hooks/check_gate.py. Run with: python3 -m unittest discover tests"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "hooks", "check_gate.py")

ROADMAP = """# Roadmap

- [x] **1. Greet:** done.
- [ ] **2. Shout:** a --shout flag.
- [ ] **3. Later:** not yet.
"""


def make_project(check_line, roadmap=ROADMAP):
    root = tempfile.mkdtemp()
    if roadmap is not None:
        with open(os.path.join(root, "ROADMAP.md"), "w") as f:
            f.write(roadmap)
    os.makedirs(os.path.join(root, "docs", "milestones"))
    if check_line is not None:
        with open(os.path.join(root, "docs", "milestones", "2-shout.md"), "w") as f:
            f.write(f"# 2. Shout\n\n## Notes\n\n## Spec\n\n{check_line}\n\n## Decisions\n")
    return root


def stop(root, last_message="Built: it"):
    event = {"hook_event_name": "SubagentStop", "agent_type": "quarterback:implementer",
             "cwd": root, "stop_hook_active": False, "last_assistant_message": last_message}
    return subprocess.run(["python3", HOOK], input=json.dumps(event), capture_output=True, text=True)


class CheckGate(unittest.TestCase):

    def project(self, *args, **kwargs):
        root = make_project(*args, **kwargs)
        self.addCleanup(shutil.rmtree, root)
        return root

    def assertBlocked(self, run):
        self.assertEqual(run.returncode, 2, run.stderr)
        self.assertIn("check fails", run.stderr)

    def assertAllowed(self, run):
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stderr, "")

    def test_passing_check_lets_it_stop(self):
        self.assertAllowed(stop(self.project("Check: `true`")))

    def test_failing_check_blocks_with_its_output(self):
        run = stop(self.project("Check: `echo 'FAILED: test_shout'; exit 1`"))
        self.assertBlocked(run)
        self.assertIn("FAILED: test_shout", run.stderr)
        self.assertIn("exit 1", run.stderr)

    def test_check_without_backticks(self):
        self.assertBlocked(stop(self.project("Check: false")))

    def test_check_runs_in_the_project(self):
        root = self.project("Check: `test -f ROADMAP.md`")
        self.assertAllowed(stop(root))

    def test_escalating_lets_it_stop(self):
        root = self.project("Check: `false`")
        self.assertAllowed(stop(root, "Built: half\nNEEDS_USER: Which?\nOptions: a | b\nDefault: a"))

    def test_check_none_lets_it_stop(self):
        self.assertAllowed(stop(self.project("Check: none")))

    def test_no_check_line_lets_it_stop(self):
        self.assertAllowed(stop(self.project("Acceptance checks: run it")))

    def test_no_milestone_file_lets_it_stop(self):
        self.assertAllowed(stop(self.project(None)))

    def test_no_roadmap_lets_it_stop(self):
        self.assertAllowed(stop(self.project("Check: `false`", roadmap=None)))

    def test_every_milestone_ticked_lets_it_stop(self):
        self.assertAllowed(stop(self.project("Check: `false`", roadmap="- [x] **2. Shout:** done.\n")))

    def test_uses_the_first_unticked_milestone(self):
        root = self.project("Check: `true`")
        with open(os.path.join(root, "docs", "milestones", "3-later.md"), "w") as f:
            f.write("Check: `false`\n")
        self.assertAllowed(stop(root))


if __name__ == "__main__":
    unittest.main()
