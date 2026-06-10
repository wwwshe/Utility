#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${MOBILE_NEWS_VENV:-$PROJECT_DIR/.venv}"
RUN_SH="$PROJECT_DIR/run.sh"
TEMPLATE="$PROJECT_DIR/launchd/com.news.daily.plist.template"
OUTPUT="$HOME/Library/LaunchAgents/com.news.daily.plist"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "템플릿을 찾을 수 없습니다: $TEMPLATE" >&2
  exit 1
fi

if [[ ! -x "$RUN_SH" ]]; then
  echo "run.sh가 없습니다. 먼저 setup.sh를 실행하세요." >&2
  exit 1
fi

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  echo "가상환경이 없습니다: $VENV_DIR" >&2
  echo "  $PROJECT_DIR/setup.sh" >&2
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"
sed \
  -e "s|__RUN_SH__|$RUN_SH|g" \
  -e "s|__VENV_DIR__|$VENV_DIR|g" \
  "$TEMPLATE" > "$OUTPUT"

ENV_FILE="$PROJECT_DIR/.env"
if [[ ! -f "$ENV_FILE" ]] || ! grep -q '^GEMINI_API_KEY=.' "$ENV_FILE" 2>/dev/null || grep -q 'your_api_key_here' "$ENV_FILE" 2>/dev/null; then
  echo "경고: .env에 GEMINI_API_KEY가 없습니다. run.sh 실행 전 .env를 설정하세요." >&2
fi

echo "생성됨: $OUTPUT"
echo "API 키는 $ENV_FILE 에서 run.sh가 자동으로 읽습니다."
echo
echo "등록:"
echo "  launchctl bootout gui/\$(id -u) \"$OUTPUT\" 2>/dev/null || true"
echo "  launchctl bootstrap gui/\$(id -u) \"$OUTPUT\""
echo "  launchctl start com.news.daily"
