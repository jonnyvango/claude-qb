"""Tests for hooks/guard_git.py. Run with: python3 -m unittest discover tests"""
import json
import os
import subprocess
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "hooks", "guard_git.py")


def sh(cwd, *args):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def make_repo(branch="spec/x", origin_head=True):
    repo = tempfile.mkdtemp()
    sh(repo, "git", "init", "-q", "-b", "master")
    sh(repo, "git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init")
    if origin_head:
        sh(repo, "git", "update-ref", "refs/remotes/origin/master", "HEAD")
        sh(repo, "git", "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/master")
    if branch != "master":
        sh(repo, "git", "switch", "-q", "-c", branch)
    os.makedirs(os.path.join(repo, "sub"))
    return repo


def decide(event):
    out = subprocess.run(["python3", HOOK], input=json.dumps(event), capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"] if out.stdout else "allow"


def bash(command, cwd):
    return decide({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": cwd})


class OnFeatureBranch(unittest.TestCase):
    repo = make_repo()

    def assertDenied(self, command):
        self.assertEqual(bash(command, self.repo), "deny", command)

    def assertAllowed(self, command):
        self.assertEqual(bash(command, self.repo), "allow", command)

    def test_push_to_default_is_denied(self):
        for command in [
            "git push origin master",
            "git push origin HEAD:master",
            "git push origin spec/x:refs/heads/master",
            "git push origin --delete master",
            "git push origin :master",
            "git push --all origin",
            "git push --mirror origin",
            "cd sub && git push origin master",
            "git -C sub push origin master",
            "git status; git push origin master",
            "GIT_TRACE=1 git push origin master",
            "bash -c 'git push origin master'",
        ]:
            self.assertDenied(command)

    def test_force_push_is_denied(self):
        for command in [
            "git push --force origin spec/x",
            "git push -f",
            "git push -uf origin spec/x",
            "git push origin +spec/x",
            "git push --force-with-lease origin spec/x",
            "git push --force-with-lease=spec/x origin spec/x",
        ]:
            self.assertDenied(command)

    def test_merging_pull_requests_is_denied(self):
        for command in [
            "gh pr merge 12 --squash",
            "gh api -X PUT repos/o/r/pulls/3/merge",
            "gh api repos/o/r/merges -f base=master -f head=spec/x",
        ]:
            self.assertDenied(command)

    def test_ordinary_work_is_allowed(self):
        for command in [
            "git push -u origin spec/x",
            "git push",
            "git push origin HEAD",
            "git push origin --tags",
            "git merge master",
            "git commit -m 'never git push origin master'",
            "echo git push origin master",
            "git log master",
            "gh pr create --base master --title t --body b",
            "gh pr view 3",
            "ls -la",
        ]:
            self.assertAllowed(command)


class OnDefaultBranch(unittest.TestCase):
    repo = make_repo(branch="master")

    def test_bare_push_is_denied(self):
        for command in ["git push", "git push -u origin HEAD", "git push origin"]:
            self.assertEqual(bash(command, self.repo), "deny", command)

    def test_merge_into_default_is_denied(self):
        self.assertEqual(bash("git merge spec/x", self.repo), "deny")
        self.assertEqual(bash("git merge --abort", self.repo), "allow")

    def test_pull_is_allowed(self):
        self.assertEqual(bash("git pull", self.repo), "allow")


class WithoutOriginHead(unittest.TestCase):
    repo = make_repo(origin_head=False)

    def test_main_and_master_are_both_protected(self):
        self.assertEqual(bash("git push origin main", self.repo), "deny")
        self.assertEqual(bash("git push origin master", self.repo), "deny")
        self.assertEqual(bash("git push origin spec/x", self.repo), "allow")


class GitHubTools(unittest.TestCase):
    repo = make_repo()

    def mcp(self, name, **tool_input):
        return decide({"tool_name": f"mcp__plugin_github_github__{name}", "tool_input": tool_input, "cwd": self.repo})

    def test_merge_tool_is_denied(self):
        self.assertEqual(self.mcp("merge_pull_request", owner="o", repo="r", pullNumber=1), "deny")

    def test_writes_to_default_are_denied(self):
        self.assertEqual(self.mcp("push_files", branch="master", files=[]), "deny")
        self.assertEqual(self.mcp("create_or_update_file", path="a", content="b"), "deny")

    def test_writes_to_branches_are_allowed(self):
        self.assertEqual(self.mcp("push_files", branch="spec/x", files=[]), "allow")


if __name__ == "__main__":
    unittest.main()
