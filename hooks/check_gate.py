#!/usr/bin/env python3
"""Quarterback's check gate, which keeps the implementer working while the
milestone's check fails.

It runs as two hooks. A subagent may end by calling the SubagentHandback tool,
and blocking SubagentStop doesn't stop that, so a PreToolUse hook on that tool
denies it. SubagentStop covers subagents that end without the tool, and skips
the check if the hand-back was already allowed. The current milestone is the first unticked one in ROADMAP.md,
its file is docs/milestones/<n>-*.md, and its command is the `Check:` line in
that file. The implementer may still stop to escalate (a NEEDS_USER report).
With no roadmap, milestone file or check line, it lets the implementer stop.
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

TIMEOUT = 540
TAIL_LINES = 40
TAIL_CHARS = 3000

BLOCKED = """The milestone's check fails, so you're not done yet.

Command: {command}
{result}
Last output:
{tail}

Fix what it shows, then report again. If the same check still fails after two genuinely different fixes, escalate as the playbook says."""


def current_milestone(cwd):
    try:
        with open(os.path.join(cwd, "ROADMAP.md"), encoding="utf-8") as f:
            roadmap = f.read()
    except OSError:
        return None
    match = re.search(r"^\s*[-*] \[ \] \*\*(\w+)\.", roadmap, re.MULTILINE)
    return match.group(1) if match else None


def git(cwd, *args):
    try:
        out = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def branch_milestone_files(cwd):
    """The milestone files this branch has changed, so ticking the roadmap early can't skip the check."""
    head = git(cwd, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    for base in [head, "origin/master", "origin/main", "master", "main"]:
        fork = base and git(cwd, "merge-base", "HEAD", base)
        if fork:
            changed = (git(cwd, "diff", "--name-only", "--relative", fork, "--", "docs/milestones/") or "").splitlines()
            changed += (git(cwd, "ls-files", "--others", "--exclude-standard", "docs/milestones/") or "").splitlines()
            return sorted({os.path.join(cwd, p) for p in changed if p.endswith(".md")})
    return []


def milestone_files(cwd):
    changed = [p for p in branch_milestone_files(cwd) if os.path.exists(p)]
    if len(changed) == 1:
        return changed
    number = current_milestone(cwd)
    return sorted(glob.glob(os.path.join(cwd, "docs", "milestones", f"{number}-*.md"))) if number else []


def check_command(cwd):
    for path in milestone_files(cwd):
        with open(path, encoding="utf-8") as f:
            match = re.search(r"^Check:\s*(.+?)\s*$", f.read(), re.MULTILINE)
        if match:
            command = match.group(1)
            if len(command) > 1 and command[0] == command[-1] == "`":
                command = command[1:-1].strip()
            return None if command.lower() in {"none", ""} else command
    return None


def tail(output):
    lines = output.rstrip().splitlines()[-TAIL_LINES:]
    return "\n".join(lines)[-TAIL_CHARS:] or "(none)"


def passed_marker(event):
    agent = re.sub(r"[^\w-]", "", str(event.get("agent_id") or ""))
    return agent and os.path.join(tempfile.gettempdir(), f"quarterback-check-passed-{agent}")


def allow(pre_tool, marker):
    """After an allowed hand-back, let the SubagentStop that follows skip the check."""
    if pre_tool and marker:
        open(marker, "w").close()


def block(event, reason):
    if event.get("hook_event_name") == "PreToolUse":
        json.dump({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}, sys.stdout)
    else:
        json.dump({"decision": "block", "reason": reason}, sys.stdout)


def main():
    event = json.load(sys.stdin)
    pre_tool = event.get("hook_event_name") == "PreToolUse"
    if pre_tool and event.get("agent_type") != "quarterback:implementer":
        return
    marker = passed_marker(event)
    if not pre_tool and marker and os.path.exists(marker):
        os.remove(marker)
        return
    report = json.dumps(event.get("tool_input")) if pre_tool else event.get("last_assistant_message")
    if "NEEDS_USER:" in (report or ""):
        allow(pre_tool, marker)
        return
    cwd = event.get("cwd") or os.getcwd()
    command = check_command(cwd)
    if not command:
        return
    try:
        run = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"") + (e.stderr or b"")
        output = out.decode(errors="replace") if isinstance(out, bytes) else out
        result = f"Result: timed out after {TIMEOUT}s"
    else:
        if run.returncode == 0:
            allow(pre_tool, marker)
            return
        output = run.stdout + run.stderr
        result = f"Result: exit {run.returncode}"
    block(event, BLOCKED.format(command=command, result=result, tail=tail(output)))


if __name__ == "__main__":
    main()
