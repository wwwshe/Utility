# Agent Common Rules Design

## Goal

Build a global utility under `agent-common-rules/` that installs shared AI-agent rules and conditional skills at the machine level.

## Scope

The utility supports:

- Codex global rules via `~/.codex/AGENTS.md`
- Claude Code global rules via `~/.claude/CLAUDE.md`
- Codex global skills via `~/.codex/skills/*/SKILL.md`
- Claude global skills via `~/.claude/skills/*/SKILL.md`
- Cursor manual setup via generated `dist/cursor-user-rule.md` whenever global rules are installed

Project-level installation is intentionally out of scope. The goal is to avoid duplicating shared policy files across repositories.

## Architecture

`agent_common_rules.py` is the core CLI and uses only the Python standard library. It loads short policy markdown files from `policy/`, loads conditional skill files from `skills/`, writes managed blocks to Codex/Claude global rule files, installs missing global skills, and generates a Cursor User Rules guide.

`install.sh` is a small wrapper that executes the Python script from the utility directory.

## Source Files

- `policy/*.md`: short always-on rules combined into global rule managed blocks
- `skills/*/SKILL.md`: conditional workflows installed into global skill directories
- `dist/cursor-user-rule.md`: generated manual setup text for Cursor User Rules

## Update Rules

- Codex/Claude global rule files are never fully overwritten.
- Managed blocks use `<!-- BEGIN agent-common-rules -->` and `<!-- END agent-common-rules -->`.
- If a managed block exists, the block is replaced.
- If no managed block exists, the block is appended.
- Global skill files are created if missing when `--global-skills` is used.
- Existing global skill files are preserved unless `--force-skills` is passed.
- Cursor is not auto-mutated; the utility writes a guide for manual User Rules setup.

## CLI

Examples:

```bash
./install.sh --global-rules all
./install.sh --global-skills all
./install.sh --global-rules all --global-skills all
./install.sh --global-rules all --global-skills all --dry-run
./install.sh --global-skills all --force-skills
```

## Testing

Tests use `unittest` and temporary directories. They verify managed-block insertion, managed-block replacement, policy/skill loading, global rule installation, global skill preservation, and Cursor guide creation.
