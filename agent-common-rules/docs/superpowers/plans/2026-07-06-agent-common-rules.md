# Agent Common Rules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `agent-common-rules/`, a dependency-free installer for machine-level AI-agent rules and skills.

**Architecture:** A Python standard-library CLI reads `policy/*.md` and `skills/*/SKILL.md`, updates Codex/Claude global rule files with managed blocks, installs missing Codex/Claude global skills, and generates Cursor manual User Rules guidance whenever global rules are installed.

**Tech Stack:** Bash, Python 3 standard library, `unittest`.

---

## File Structure

- Create `agent-common-rules/agent_common_rules.py`: CLI, policy/skill loading, managed-block replacement, global rule install, global skill install, Cursor guide generation.
- Create `agent-common-rules/install.sh`: shell wrapper around the Python CLI.
- Create `agent-common-rules/policy/*.md`: short always-on global rule sources.
- Create `agent-common-rules/skills/*/SKILL.md`: conditional global skill sources.
- Create `agent-common-rules/README.md`: usage, installed files, safety behavior.
- Create `tests/test_agent_common_rules.py`: unit tests using temporary directories.
- Modify `README.md`: add the new utility to the root project list and structure.

## Tasks

### Task 1: Core Installer Tests

**Files:**
- Create: `tests/test_agent_common_rules.py`

- [ ] Write tests for marker insertion, marker replacement, policy/skill loading, global rule install, global skill install, preservation behavior, dry-run behavior, and Cursor guide generation.
- [ ] Run `python3 -m unittest tests/test_agent_common_rules.py -v` and confirm it fails because `agent_common_rules` does not exist.

### Task 2: Core Installer Implementation

**Files:**
- Create: `agent-common-rules/agent_common_rules.py`
- Create: `agent-common-rules/policy/*.md`
- Create: `agent-common-rules/skills/*/SKILL.md`

- [ ] Implement CLI parsing for `--global-rules`, `--global-skills`, `--dry-run`, and `--force-skills`.
- [ ] Implement managed block insertion and replacement.
- [ ] Implement policy and skill source loading.
- [ ] Implement Codex/Claude global rule installation.
- [ ] Implement Codex/Claude global skill installation.
- [ ] Implement Cursor User Rules guide generation.
- [ ] Run `python3 -m unittest tests/test_agent_common_rules.py -v` and confirm tests pass.

### Task 3: Shell Wrapper and Docs

**Files:**
- Create: `agent-common-rules/install.sh`
- Create: `agent-common-rules/README.md`
- Modify: `README.md`

- [ ] Add a Bash wrapper that executes the Python CLI from the utility directory.
- [ ] Document global rule, global skill, and Cursor guide usage.
- [ ] Add `agent-common-rules` to the root README.
- [ ] Run `bash agent-common-rules/install.sh --help`.
- [ ] Run dry-runs for global rules, global skills, and Cursor guide.

### Task 4: Final Verification

**Files:**
- Verify all files from previous tasks.

- [ ] Run `python3 -m unittest tests/test_agent_common_rules.py -v`.
- [ ] Run `bash agent-common-rules/install.sh --global-rules all --global-skills all --dry-run`.
- [ ] Check `git status --short` and confirm only intended files plus pre-existing unrelated files are present.
