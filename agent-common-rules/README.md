# agent-common-rules

이 맥북의 AI agent 전역 규칙과 전역 skill을 설치하고 갱신하는 유틸리티입니다.

Codex와 Claude Code에는 파일 기반 전역 규칙과 전역 skill을 설치합니다. Cursor는 안정적인 전역 rule 파일 경로가 없으므로, 사용자가 Cursor 설정에 붙여넣을 수 있는 안내 파일을 생성합니다.

짧은 상시 정책 원본은 `policy/*.md`에 두고, 조건부 절차는 `skills/*/SKILL.md`에 둡니다.

## 설치 대상

전역 위치에 아래 파일을 생성하거나 갱신합니다.

| 파일 | 동작 |
|------|------|
| `~/.codex/AGENTS.md` | managed block 추가/교체 |
| `~/.claude/CLAUDE.md` | managed block 추가/교체 |
| `~/.codex/skills/*/SKILL.md` | 없으면 생성, 기존 파일은 기본 보존 |
| `~/.claude/skills/*/SKILL.md` | 없으면 생성, 기존 파일은 기본 보존 |
| `dist/cursor-user-rule.md` | Cursor User Rules에 붙여넣을 안내 파일 생성 |

## 기본 정책과 Skills

`policy/` 아래 짧은 정책 파일은 Codex/Claude 전역 규칙 managed block에 합쳐서 넣습니다.

| 정책 | 내용 |
|------|------|
| `core.md` | 상시 적용되는 짧은 핵심 원칙 |
| `git-safety.md` | 사용자 변경 보호, 위험한 git 작업 전 확인 |
| `secrets-and-privacy.md` | API 키, 토큰, private data 보호 |
| `communication-style.md` | 한국어 우선, 간결한 진행/결과 보고 |

`skills/` 아래 조건부 절차는 `--global-skills` 옵션으로 Codex/Claude 전역 skill 디렉터리에 설치합니다.

| Skill | 사용 시점 |
|-------|----------|
| `dependency-change` | 의존성 추가/설치/업데이트/lockfile 변경 |
| `filesystem-editing` | 파일 편집, 삭제, 이동, 대량 생성/갱신 |
| `source-verification` | 조사, 최신 정보, API/패키지 버전, 출처 기반 답변 |
| `swift-concurrency` | Swift async/await, MainActor, UIKit/SwiftUI ViewModel, Combine |

## 사용법

Codex/Claude 전역 규칙 설치:

```bash
cd /Volumes/500G/workspace/Utility/agent-common-rules
./install.sh --global-rules all
```

Codex/Claude 전역 skill 설치:

```bash
./install.sh --global-skills all
```

기본 실행은 Codex/Claude 전역 rules, Codex/Claude 전역 skills, Cursor 안내 파일을 모두 처리합니다.

```bash
./install.sh
```

명시적으로 한 번에 적용:

```bash
./install.sh --global-rules all --global-skills all
```

쓰기 전에 변경 예정 파일 확인:

```bash
./install.sh --global-rules all --global-skills all --dry-run
```

개별 대상만 설치:

```bash
./install.sh --global-rules codex
./install.sh --global-rules claude
./install.sh --global-skills codex
./install.sh --global-skills claude
```

기존 전역 skill까지 교체:

```bash
./install.sh --global-skills all --force-skills
```

## 안전장치

Codex/Claude 전역 규칙 파일은 전체 덮어쓰지 않습니다. 아래 marker 사이의 블록만 이 유틸리티가 관리합니다.

```markdown
<!-- BEGIN agent-common-rules -->
...
<!-- END agent-common-rules -->
```

기존 전역 skill 파일은 기본적으로 보존합니다. 원본 내용으로 교체하려면 `--force-skills`를 명시해야 합니다.

Cursor는 자동 설치하지 않습니다. `dist/cursor-user-rule.md` 내용을 Cursor Settings > Rules > User Rules에 직접 붙여넣습니다.
