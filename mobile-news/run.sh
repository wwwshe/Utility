#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="${MOBILE_NEWS_VENV:-$PROJECT_DIR/.venv}"
PYTHON="$VENV_DIR/bin/python"
ENV_FILE="$PROJECT_DIR/.env"
SCRIPT_NAME="${1:-daily_news.py}"
shift || true

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi

if [[ ! -x "$PYTHON" ]]; then
  echo "가상환경이 없습니다. 먼저 setup.sh를 실행하세요." >&2
  echo "  $PROJECT_DIR/setup.sh" >&2
  exit 1
fi

case "$SCRIPT_NAME" in
  daily_news.py)
    if [[ -z "${GEMINI_API_KEY:-}" ]]; then
      echo "GEMINI_API_KEY가 없습니다. .env 파일을 설정하세요." >&2
      echo "  $ENV_FILE" >&2
      exit 1
    fi
    exec "$PYTHON" "$PROJECT_DIR/$SCRIPT_NAME" "$@"
    ;;
  test_notification.py)
    exec "$PYTHON" "$PROJECT_DIR/$SCRIPT_NAME" "$@"
    ;;
  *)
    echo "지원하지 않는 스크립트: $SCRIPT_NAME" >&2
    echo "사용 가능: daily_news.py, test_notification.py" >&2
    exit 1
    ;;
esac
