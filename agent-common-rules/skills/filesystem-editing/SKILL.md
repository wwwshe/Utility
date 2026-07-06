---
name: filesystem-editing
description: Use when editing, deleting, moving, generating, or bulk-updating files, especially when existing user changes or generated files may be present.
---

# Filesystem Editing

Prevent accidental data loss and keep edits scoped.

## Before Editing

- Check whether the file already contains user changes.
- If unrelated user edits exist, work around them instead of reverting them.
- If the requested change conflicts with existing user edits, stop and ask.

## Editing

- Prefer narrow edits to files directly related to the task.
- Preserve existing structure and project conventions unless a change is required.
- Do not rewrite whole files when a smaller patch is enough.
- Do not modify generated output, dependency directories, build artifacts, caches, or vendored code unless explicitly requested.
- Use managed marker blocks for repeated generated guidance.

## Deletion

Ask before deleting files or directories unless all are true:

- The file was created by the agent in the current task.
- The file is clearly temporary.
- The deletion is needed to finish the requested task.
