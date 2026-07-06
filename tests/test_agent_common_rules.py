import tempfile
import unittest
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "agent-common-rules"))

import agent_common_rules


def sample_sources():
    return {
        "policies": {"core.md": "core policy"},
        "skills": {"dependency-change/SKILL.md": "dependency skill"},
    }


class AgentCommonRulesTests(unittest.TestCase):
    def test_load_sources_reads_policy_and_skill_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            policy_dir = root / "policy"
            skills_dir = root / "skills"
            policy_dir.mkdir()
            (skills_dir / "dependency-change").mkdir(parents=True)
            (policy_dir / "core.md").write_text("core policy", encoding="utf-8")
            (skills_dir / "dependency-change" / "SKILL.md").write_text("dependency skill", encoding="utf-8")

            sources = agent_common_rules.load_sources(
                policy_dir=policy_dir,
                skills_dir=skills_dir,
            )

            self.assertEqual(sources["policies"], {"core.md": "core policy"})
            self.assertEqual(sources["skills"], {"dependency-change/SKILL.md": "dependency skill"})

    def test_insert_managed_block_into_new_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "AGENTS.md"

            result = agent_common_rules.upsert_managed_block(target, "hello", dry_run=False)

            self.assertEqual(result, "created")
            text = target.read_text(encoding="utf-8")
            self.assertIn("<!-- BEGIN agent-common-rules -->", text)
            self.assertIn("hello", text)
            self.assertIn("<!-- END agent-common-rules -->", text)

    def test_replace_existing_managed_block_without_touching_other_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "CLAUDE.md"
            target.write_text(
                "# Existing\n\n"
                "<!-- BEGIN agent-common-rules -->\nold\n<!-- END agent-common-rules -->\n\n"
                "Keep me\n",
                encoding="utf-8",
            )

            result = agent_common_rules.upsert_managed_block(target, "new", dry_run=False)

            self.assertEqual(result, "updated")
            text = target.read_text(encoding="utf-8")
            self.assertIn("# Existing", text)
            self.assertIn("Keep me", text)
            self.assertIn("new", text)
            self.assertNotIn("old", text)

    def test_global_skill_files_are_installed_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "codex-skills"

            changes = agent_common_rules.install_global_skills(
                home,
                skills={"dependency-change/SKILL.md": "dependency skill"},
                dry_run=False,
                force=False,
            )

            skill = home / "dependency-change" / "SKILL.md"
            self.assertEqual(skill.read_text(encoding="utf-8"), "dependency skill\n")
            self.assertIn(("created", skill.resolve()), changes)

    def test_existing_global_skill_is_preserved_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "codex-skills"
            skill = home / "dependency-change" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("custom skill\n", encoding="utf-8")

            changes = agent_common_rules.install_global_skills(
                home,
                skills={"dependency-change/SKILL.md": "dependency skill"},
                dry_run=False,
                force=False,
            )

            self.assertEqual(skill.read_text(encoding="utf-8"), "custom skill\n")
            self.assertIn(("preserved", skill.resolve()), changes)

    def test_global_rules_are_installed_with_managed_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "AGENTS.md"

            changes = agent_common_rules.install_global_rule_file(
                target,
                content="global rule",
                dry_run=False,
            )

            text = target.read_text(encoding="utf-8")
            self.assertIn("<!-- BEGIN agent-common-rules -->", text)
            self.assertIn("global rule", text)
            self.assertIn(("created", target.resolve()), changes)

    def test_cursor_guide_is_written_for_manual_user_rule_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "cursor-user-rule.md"

            changes = agent_common_rules.write_cursor_user_rule_guide(
                output,
                content="cursor user rule",
                dry_run=False,
            )

            self.assertEqual(output.read_text(encoding="utf-8"), "cursor user rule\n")
            self.assertIn(("created", output.resolve()), changes)

    def test_default_actions_install_all_global_targets(self):
        parser = agent_common_rules.build_parser()

        args = agent_common_rules.resolve_default_actions(parser.parse_args([]))

        self.assertEqual(args.global_rules, "all")
        self.assertEqual(args.global_skills, "all")
        self.assertTrue(agent_common_rules.should_write_cursor_guide(args))

    def test_global_rules_action_writes_cursor_guide(self):
        parser = agent_common_rules.build_parser()

        args = agent_common_rules.resolve_default_actions(parser.parse_args(["--global-rules", "all"]))

        self.assertEqual(args.global_rules, "all")
        self.assertTrue(agent_common_rules.should_write_cursor_guide(args))

    def test_cursor_guide_notice_mentions_settings_and_path(self):
        message = agent_common_rules.cursor_guide_notice(Path("/tmp/cursor-user-rule.md"))

        self.assertIn("Cursor 설정 안내", message)
        self.assertIn("Cursor Settings > Rules > User Rules", message)
        self.assertIn("/tmp/cursor-user-rule.md", message)

    def test_cursor_user_rule_content_has_korean_guide_and_english_rules(self):
        content = agent_common_rules.cursor_user_rule_content(
            "# Shared AI Agent Global Rules\n\n"
            "- Keep edits scoped."
        )

        self.assertIn("# Cursor 사용자 Rule", content)
        self.assertIn("복사해 넣으세요", content)
        self.assertIn("# Shared AI Agent Global Rules", content)
        self.assertIn("- Keep edits scoped.", content)


if __name__ == "__main__":
    unittest.main()
