#!/usr/bin/env python3
"""Quarterback's git guard, a PreToolUse hook.

Denies merging pull requests, merging into the default branch, pushing to the
default branch and force-pushing. It catches mistakes, not a determined bypass.
"""
import json
import os
import re
import shlex
import subprocess
import sys

NEVER_MERGE = "Quarterback never merges. Open a pull request and leave the merge to the user."
NEVER_DEFAULT = "Quarterback never pushes to the default branch ({}). Push a ticket/* or spec/* branch and open a pull request."
NEVER_FORCE = "Quarterback never force-pushes. Add a new commit instead."

OPERATORS = {"&&", "||", ";", "|", "&", "(", ")", "|&", ";;"}
WRAPPERS = {"sudo", "command", "env", "time", "nohup", "exec", "builtin"}
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"}
PUSH_OPTS_WITH_VALUE = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}


def git(cwd, *args):
    try:
        out = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def default_branches(cwd):
    head = git(cwd, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if head:
        return {head.split("/", 1)[-1]}
    configured = git(cwd, "config", "init.defaultBranch")
    return {"main", "master"} | ({configured} if configured else set())


def tokenize(command):
    try:
        lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return re.findall(r"&&|\|\||[;&|()]|[^\s;&|()]+", command)


def segments(tokens):
    current = []
    for token in tokens:
        if token in OPERATORS:
            if current:
                yield current
            current = []
        else:
            current.append(token)
    if current:
        yield current


def strip_prefix(words):
    i = 0
    while i < len(words) and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[i]) or words[i] in WRAPPERS):
        i += 1
    return words[i:]


def branch_name(ref):
    return ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref


def check_push(args, cwd):
    positional, everything = [], False
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in PUSH_OPTS_WITH_VALUE:
            i += 2
            continue
        if arg in ("--force", "--force-with-lease") or arg.startswith("--force-with-lease="):
            return NEVER_FORCE
        if arg in ("--all", "--mirror", "--branches"):
            everything = True
        elif re.match(r"^-[a-zA-Z0-9]+$", arg) and "f" in arg:
            return NEVER_FORCE
        elif not arg.startswith("-"):
            positional.append(arg)
        i += 1

    defaults = default_branches(cwd)
    blocked = NEVER_DEFAULT.format(" or ".join(sorted(defaults)))
    if everything:
        return blocked
    refspecs = positional[1:]
    if any(ref.startswith("+") for ref in refspecs):
        return NEVER_FORCE
    current = git(cwd, "branch", "--show-current")
    if not refspecs:
        return blocked if current in defaults else None
    for ref in refspecs:
        dst = ref.split(":", 1)[-1]
        dst = current if dst == "HEAD" else branch_name(dst)
        if dst in defaults:
            return blocked
    return None


def check_git(args, cwd):
    i = 0
    while i < len(args) and args[i].startswith("-"):
        if args[i] == "-C" and i + 1 < len(args):
            cwd = os.path.join(cwd, os.path.expanduser(args[i + 1]))
        i += 2 if args[i] in GIT_OPTS_WITH_VALUE else 1
    if i >= len(args):
        return None
    sub, rest = args[i], args[i + 1:]
    if sub == "push":
        return check_push(rest, cwd)
    if sub == "merge" and not {"--abort", "--quit"} & set(rest):
        if git(cwd, "branch", "--show-current") in default_branches(cwd):
            return NEVER_MERGE
    return None


def check_gh(args):
    if args[:2] == ["pr", "merge"]:
        return NEVER_MERGE
    if args[:1] == ["api"] and any(re.search(r"/pulls/\d+/merge\b|/merges\b", a) for a in args):
        return NEVER_MERGE
    return None


def check_command(command, cwd, depth=0):
    for words in segments(tokenize(command)):
        words = strip_prefix(words)
        if not words:
            continue
        name = os.path.basename(words[0])
        if name == "cd" and len(words) > 1:
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        reason = None
        if name == "git":
            reason = check_git(words[1:], cwd)
        elif name == "gh":
            reason = check_gh(words[1:])
        elif depth < 2:
            for word in words[1:]:
                if re.search(r"\b(git|gh)\s", word):
                    reason = check_command(word, cwd, depth + 1)
                    if reason:
                        break
        if reason:
            return reason
    return None


def check_mcp(tool, tool_input, cwd):
    if tool.endswith("merge_pull_request"):
        return NEVER_MERGE
    branch = tool_input.get("branch") or ""
    defaults = default_branches(cwd)
    if not branch or branch_name(branch) in defaults:
        return NEVER_DEFAULT.format(branch or "the default branch")
    return None


def main():
    event = json.load(sys.stdin)
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    cwd = event.get("cwd") or os.getcwd()
    if tool == "Bash":
        command = tool_input.get("command", "")
        reason = check_command(command, cwd) if re.search(r"\b(git|gh)\b", command) else None
    elif tool.startswith("mcp__"):
        reason = check_mcp(tool, tool_input, cwd)
    else:
        reason = None
    if reason:
        json.dump({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}, sys.stdout)


if __name__ == "__main__":
    main()
