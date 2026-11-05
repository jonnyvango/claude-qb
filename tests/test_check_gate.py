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


def setUpModule():
    global MARKERS
    MARKERS = tempfile.mkdtemp()
    unittest.addModuleCleanup(shutil.rmtree, MARKERS)


def run_hook(event):
    env = {**os.environ, "TMPDIR": MARKERS}
    run = subprocess.run(["python3", HOOK], input=json.dumps(event), capture_output=True, text=True, env=env)
    if run.returncode != 0:
        raise AssertionError(run.stderr)
    return json.loads(run.stdout) if run.stdout else None


def stop(root, last_message="Built: it", agent_id="a1"):
    return run_hook({"hook_event_name": "SubagentStop", "agent_type": "quarterback:implementer",
                     "agent_id": agent_id, "cwd": root, "stop_hook_active": False,
                     "last_assistant_message": last_message})


def hand_back(root, report="Built: it", agent_type="quarterback:implementer", agent_id="a1"):
    return run_hook({"hook_event_name": "PreToolUse", "tool_name": "SubagentHandback",
                     "agent_type": agent_type, "agent_id": agent_id, "cwd": root,
                     "tool_input": {"report": report}})


def reason(decision):
    if decision is None:
        return None
    if "hookSpecificOutput" in decision:
        out = decision["hookSpecificOutput"]
        return out["permissionDecisionReason"] if out["permissionDecision"] == "deny" else None
    return decision["reason"] if decision.get("decision") == "block" else None


class CheckGate(unittest.TestCase):

    def project(self, *args, **kwargs):
        root = make_project(*args, **kwargs)
        self.addCleanup(shutil.rmtree, root)
        return root

    def assertBlocked(self, decision):
        self.assertIn("check fails", reason(decision) or "")

    def assertAllowed(self, decision):
        self.assertIsNone(reason(decision), decision)

    def test_passing_check_lets_it_stop(self):
        self.assertAllowed(stop(self.project("Check: `true`")))

    def test_failing_check_blocks_with_its_output(self):
        decision = stop(self.project("Check: `echo 'FAILED: test_shout'; exit 1`"))
        self.assertBlocked(decision)
        self.assertIn("FAILED: test_shout", reason(decision))
        self.assertIn("exit 1", reason(decision))

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

    def test_ticking_the_roadmap_early_doesnt_skip_the_check(self):
        root = self.project(None, roadmap="- [ ] **2. Shout:** a --shout flag.\n")
        for args in [["init", "-q", "-b", "master"], ["add", "-A"],
                     ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"],
                     ["switch", "-qc", "spec/2-shout"]]:
            subprocess.run(["git", "-C", root, *args], check=True)
        with open(os.path.join(root, "docs", "milestones", "2-shout.md"), "w") as f:
            f.write("Check: `false`\n")
        with open(os.path.join(root, "ROADMAP.md"), "w") as f:
            f.write("- [x] **2. Shout:** a --shout flag.\n")
        self.assertBlocked(stop(root))

    def test_failing_check_denies_the_hand_back(self):
        root = self.project("Check: `false`")
        decision = hand_back(root, agent_id="deny")
        self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertBlocked(decision)

    def test_passing_check_allows_the_hand_back(self):
        self.assertAllowed(hand_back(self.project("Check: `true`"), agent_id="allow"))

    def test_escalating_hand_back_is_allowed(self):
        root = self.project("Check: `false`")
        self.assertAllowed(hand_back(root, "Built: half\nNEEDS_USER: Which?", agent_id="esc"))

    def test_other_agents_hand_back_freely(self):
        root = self.project("Check: `false`")
        self.assertAllowed(hand_back(root, agent_type="quarterback:reviewer", agent_id="rev"))

    def test_check_runs_once_when_the_hand_back_passed_it(self):
        log = os.path.join(self.project(None), "runs")
        root = self.project(f"Check: `echo run >> {log}`")
        hand_back(root, agent_id="once")
        self.assertAllowed(stop(root, agent_id="once"))
        with open(log) as f:
            self.assertEqual(f.read().count("run"), 1)

    def test_check_skipped_at_stop_after_an_escalating_hand_back(self):
        log = os.path.join(self.project(None), "runs")
        root = self.project(f"Check: `echo run >> {log}; false`")
        hand_back(root, "NEEDS_USER: Which?", agent_id="esc-stop")
        self.assertAllowed(stop(root, "", agent_id="esc-stop"))
        self.assertFalse(os.path.exists(log))

    def test_a_passed_hand_back_skips_only_one_stop(self):
        root = self.project("Check: `true`")
        hand_back(root, agent_id="first")
        stop(root, agent_id="first")
        with open(os.path.join(root, "docs", "milestones", "2-shout.md"), "w") as f:
            f.write("Check: `false`\n")
        self.assertBlocked(stop(root, agent_id="first"))


if __name__ == "__main__":
    unittest.main()
