---
name: dependency-change
description: Use when adding, removing, installing, upgrading, or changing package dependencies, lockfiles, package managers, build tools, or external libraries.
---

# Dependency Change

Keep dependency changes intentional, explainable, and easy to review.

## Rules

- Ask before adding a new production dependency.
- Prefer the project's existing libraries and standard library features when sufficient.
- Explain why the dependency is needed and what alternative was considered.
- Use the package manager already used by the project.
- Do not switch package managers without explicit user approval.
- Keep lockfile changes paired with the manifest change that caused them.
- Do not run broad upgrade commands unless the user asked for upgrades.
- When installation requires network access or modifies global/user-level state, ask before proceeding and state what will be installed.
