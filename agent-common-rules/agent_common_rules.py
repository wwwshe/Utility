#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


BEGIN_MARKER = "<!-- BEGIN agent-common-rules -->"
END_MARKER = "<!-- END agent-common-rules -->"

SCRIPT_DIR = Path(__file__).resolve().parent
POLICY_DIR = SCRIPT_DIR / "policy"
SKILLS_DIR = SCRIPT_DIR / "skills"

GLOBAL_RULE_TARGETS = {
    "codex": Path.home() / ".codex" / "AGENTS.md",
    "claude": Path.home() / ".claude" / "CLAUDE.md",
}

CURSOR_GUIDE_TARGET = SCRIPT_DIR / "dist" / "cursor-user-rule.md"

Change = tuple[str, Path]


def managed_block(content: str) -> str:
    body = content.strip()
    return f"{BEGIN_MARKER}\n{body}\n{END_MARKER}\n"


def upsert_managed_block(path: Path, content: str, dry_run: bool) -> str:
    block = managed_block(content)
    if not path.exists():
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(block, encoding="utf-8")
        return "created"

    original = path.read_text(encoding="utf-8")
    start = original.find(BEGIN_MARKER)
    end = original.find(END_MARKER)

    if start != -1 and end != -1 and start < end:
        end += len(END_MARKER)
        updated = original[:start] + block.rstrip("\n") + original[end:]
        action = "updated"
    else:
        separator = "\n\n" if original.strip() else ""
        updated = original.rstrip() + separator + block
        action = "updated"

    if not dry_run and updated != original:
        path.write_text(updated, encoding="utf-8")
    return action


def install_global_skills(
    skills_root: Path,
    skills: dict[str, str],
    dry_run: bool,
    force: bool,
) -> list[Change]:
    skills_root = skills_root.expanduser().resolve()
    changes: list[Change] = []
    for relative_name, content in skills.items():
        skill_path = skills_root / relative_name
        if skill_path.exists() and not force:
            changes.append(("preserved", skill_path))
            continue

        action = "update" if skill_path.exists() else "create"
        if not dry_run:
            skill_path.parent.mkdir(parents=True, exist_ok=True)
            skill_path.write_text(content.rstrip() + "\n", encoding="utf-8")
            action = "updated" if action == "update" else "created"
        changes.append((action, skill_path))
    return changes


def render_global_rule_content(policies: dict[str, str]) -> str:
    sections = ["# Shared AI Agent Global Rules\n"]
    for filename, content in policies.items():
        sections.append(f"\n<!-- source: policy/{filename} -->\n")
        sections.append(content.strip())
        sections.append("\n")

    sections.append(
        "\n## Conditional Skills\n\n"
        "Use globally installed skills only when relevant:\n"
        "- Dependency changes: `dependency-change`\n"
        "- File editing, deletion, or bulk updates: `filesystem-editing`\n"
        "- Research, latest facts, APIs, package versions, or source-backed answers: `source-verification`\n"
        "- Swift code involving async/await, MainActor, UIKit/SwiftUI ViewModels, or Combine: `swift-concurrency`\n"
    )
    return "\n".join(sections).strip() + "\n"


def install_global_rule_file(path: Path, content: str, dry_run: bool) -> list[Change]:
    action = upsert_managed_block(path.expanduser().resolve(), content, dry_run)
    if dry_run:
        action = "create" if action == "created" else "update"
    return [(action, path.expanduser().resolve())]


def global_rule_targets(selection: str) -> list[tuple[str, Path]]:
    if selection == "all":
        return list(GLOBAL_RULE_TARGETS.items())
    return [(selection, GLOBAL_RULE_TARGETS[selection])]


def cursor_user_rule_content(global_rule_content: str) -> str:
    return (
        "# Cursor 사용자 Rule\n\n"
        "아래 코드 블록 안의 rule 본문을 Cursor Settings > Rules > User Rules에 복사해 넣으세요.\n\n"
        "Cursor는 이 installer가 안전하게 갱신할 수 있는 안정적인 User Rules 파일 경로를 제공하지 않으므로, 수동으로 붙여넣어야 합니다.\n\n"
        "```markdown\n"
        f"{global_rule_content.strip()}\n"
        "```\n"
    )


def write_cursor_user_rule_guide(path: Path, content: str, dry_run: bool) -> list[Change]:
    path = path.expanduser().resolve()
    action = "update" if path.exists() else "create"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        action = "updated" if action == "update" else "created"
    return [(action, path)]


def cursor_guide_notice(path: Path) -> str:
    return (
        "\nCursor 설정 안내: "
        f"{path.expanduser().resolve()} 파일 내용을 "
        "Cursor Settings > Rules > User Rules에 복사해 넣으세요."
    )


def load_sources(
    policy_dir: Path = POLICY_DIR,
    skills_dir: Path = SKILLS_DIR,
) -> dict[str, object]:
    policy_files = sorted(path for path in policy_dir.glob("*.md") if path.is_file())
    if not policy_files:
        raise FileNotFoundError(f"no policy markdown files found in {policy_dir}")

    sources = {
        "policies": {
            policy_path.name: policy_path.read_text(encoding="utf-8")
            for policy_path in policy_files
        },
        "skills": load_skill_files(skills_dir),
    }
    return sources


def load_skill_files(skills_dir: Path) -> dict[str, str]:
    if not skills_dir.exists():
        return {}

    skill_files = sorted(path for path in skills_dir.glob("*/SKILL.md") if path.is_file())
    return {
        str(skill_path.relative_to(skills_dir)): skill_path.read_text(encoding="utf-8")
        for skill_path in skill_files
    }


def global_skill_roots(selection: str) -> list[tuple[str, Path]]:
    home = Path.home()
    roots: dict[str, Path] = {
        "codex": home / ".codex" / "skills",
        "claude": home / ".claude" / "skills",
    }
    if selection == "all":
        return list(roots.items())
    return [(selection, roots[selection])]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install shared AI-agent global rules and skills.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without writing files.")
    parser.add_argument(
        "--global-skills",
        choices=("codex", "claude", "all"),
        help="Install missing skills into the selected global skill directory.",
    )
    parser.add_argument(
        "--force-skills",
        action="store_true",
        help="Replace existing global skill files when used with --global-skills.",
    )
    parser.add_argument(
        "--global-rules",
        choices=("codex", "claude", "all"),
        help="Install shared global rules into Codex and/or Claude global instruction files and write the Cursor guide.",
    )
    return parser


def resolve_default_actions(args: argparse.Namespace) -> argparse.Namespace:
    if not args.global_skills and not args.global_rules:
        args.global_skills = "all"
        args.global_rules = "all"
    return args


def should_write_cursor_guide(args: argparse.Namespace) -> bool:
    return bool(args.global_rules)


def print_changes(root: Path, changes: list[Change]) -> None:
    print(f"\n{root}")
    for action, path in changes:
        try:
            display_path = path.relative_to(root)
        except ValueError:
            display_path = path
        print(f"  {action:9} {display_path}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = resolve_default_actions(parser.parse_args(argv))

    sources = load_sources()
    policies = sources.get("policies", {})
    if not isinstance(policies, dict):
        raise TypeError("sources['policies'] must be a dictionary")
    skills = sources.get("skills", {})
    if not isinstance(skills, dict):
        raise TypeError("sources['skills'] must be a dictionary")
    global_rule_content = render_global_rule_content(policies)

    if args.global_rules:
        for label, target in global_rule_targets(args.global_rules):
            changes = install_global_rule_file(target, global_rule_content, args.dry_run)
            print_changes(target.expanduser().resolve().parent, changes)

    if should_write_cursor_guide(args):
        changes = write_cursor_user_rule_guide(
            CURSOR_GUIDE_TARGET,
            cursor_user_rule_content(global_rule_content),
            args.dry_run,
        )
        print_changes(CURSOR_GUIDE_TARGET.parent.resolve(), changes)
        print(cursor_guide_notice(CURSOR_GUIDE_TARGET))

    if args.global_skills:
        for label, root in global_skill_roots(args.global_skills):
            changes = install_global_skills(root, skills, args.dry_run, args.force_skills)
            print_changes(root.expanduser().resolve(), changes)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
