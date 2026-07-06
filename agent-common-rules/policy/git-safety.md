# Git Safety Policy

## Purpose

Protect user work and repository history while allowing normal development flow.

## Required Checks

- Run or inspect `git status` before making commits, branch changes, resets, cleans, or destructive file operations.
- Treat uncommitted changes as user-owned unless the user clearly says they were created by the agent.
- Do not revert, overwrite, or discard changes you did not make without explicit user approval.
- If unrelated files are modified, leave them alone and mention them separately when useful.

## Ask Before Proceeding

Ask the user before running operations that can discard work, rewrite history, or remove files, including:

- `git reset --hard`
- `git checkout -- <path>` or `git restore <path>` for files the agent did not create
- `git clean`
- force push
- branch deletion
- commit amend when the existing commit may not be agent-owned
- deleting files or directories outside the immediate task scope

When asking, state what will be affected and why the operation is needed.

## Normal Operations

The agent may run read-only git commands without asking, such as:

- `git status`
- `git diff`
- `git log`
- `git show`
- `git branch --show-current`

The agent may stage or commit only when the user requested a commit or when the current workflow explicitly requires it.
