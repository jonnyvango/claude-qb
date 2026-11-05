#!/usr/bin/env python3
"""Quarterback's check gate, a SubagentStop hook for the implementer.

Runs the current milestone's check command and keeps the implementer working
while it fails. The current milestone is the first unticked one in ROADMAP.md,
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


def check_command(cwd, number):
    for path in sorted(glob.glob(os.path.join(cwd, "docs", "milestones", f"{number}-*.md"))):
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


def main():
    event = json.load(sys.stdin)
    if "NEEDS_USER:" in (event.get("last_assistant_message") or ""):
        return
    cwd = event.get("cwd") or os.getcwd()
    number = current_milestone(cwd)
    command = number and check_command(cwd, number)
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
            return
        output = run.stdout + run.stderr
        result = f"Result: exit {run.returncode}"
    print(BLOCKED.format(command=command, result=result, tail=tail(output)), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
