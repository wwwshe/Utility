#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="${MOBILE_NEWS_VENV:-$PROJECT_DIR/.venv}"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"
REGISTER_LAUNCHD="ask"
SKIP_BREW=0

usage() {
  cat <<EOF
사용법: ./setup.sh [옵션]

옵션:
  --yes              질문 없이 진행 (launchd 등록 포함)
  --no-launchd       launchd 등록 건너뛰기
  --skip-brew        Homebrew 설치 단계 건너뛰기
  -h, --help         도움말
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) REGISTER_LAUNCHD="yes" ;;
    --no-launchd) REGISTER_LAUNCHD="no" ;;
    --skip-brew) SKIP_BREW=1 ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "알 수 없는 옵션: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

step() {
  echo
  echo "==> $1"
}

herald_app_path() {
  if [[ -d "/opt/homebrew/opt/herald/Herald.app" ]]; then
    echo "/opt/homebrew/opt/herald/Herald.app"
  elif [[ -d "/usr/local/opt/herald/Herald.app" ]]; then
    echo "/usr/local/opt/herald/Herald.app"
  fi
}

ensure_executable() {
  step "실행 권한 설정"
  chmod +x "$PROJECT_DIR/setup.sh" "$PROJECT_DIR/run.sh" "$PROJECT_DIR/launchd/install_launchd.sh"
}

ensure_brew_deps() {
  if [[ "$SKIP_BREW" -eq 1 ]]; then
    echo "Homebrew 설치 단계 건너뜀 (--skip-brew)"
    return
  fi

  step "Homebrew 의존성 확인"

  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew가 없습니다. python3와 herald는 직접 설치해 주세요." >&2
    return
  fi

  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 설치 중..."
    brew install python3
  else
    echo "python3: $(command -v python3)"
  fi

  if ! command -v herald >/dev/null 2>&1; then
    echo "herald 설치 중..."
    brew install mdsakalu/tap/herald
  else
    echo "herald: $(command -v herald)"
  fi
}

ensure_python() {
  step "Python 확인"
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3가 필요합니다." >&2
    echo "  brew install python3" >&2
    exit 1
  fi
  echo "python3: $(python3 --version) ($(command -v python3))"
}

setup_herald_permission() {
  step "Herald 알림 권한 요청"
  local herald_app
  herald_app="$(herald_app_path || true)"

  if [[ -z "$herald_app" ]]; then
    echo "Herald.app을 찾을 수 없습니다. herald 설치 후 다시 시도하세요."
    return
  fi

  echo "Herald.app 실행 중: $herald_app"
  open "$herald_app" || true
  echo "팝업이 뜨면 '허용'을 눌러 주세요."
  echo "이미 허용했다면 이 단계는 건너뛰어도 됩니다."
}

setup_venv() {
  step "Python 가상환경 설정"
  echo "프로젝트: $PROJECT_DIR"
  echo "가상환경: $VENV_DIR"

  python3 -m venv "$VENV_DIR"
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
  python -m pip install --upgrade pip
  pip install -r "$PROJECT_DIR/requirements.txt"
  echo "가상환경 준비 완료"
}

setup_env_file() {
  step "Gemini API 키 설정 (.env)"

  if [[ -f "$ENV_FILE" ]] && grep -q '^GEMINI_API_KEY=.' "$ENV_FILE" 2>/dev/null; then
    echo ".env 파일이 이미 있습니다: $ENV_FILE"
    return
  fi

  if [[ -n "${GEMINI_API_KEY:-}" ]]; then
    printf 'GEMINI_API_KEY=%s\n' "$GEMINI_API_KEY" > "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    echo ".env 파일을 생성했습니다. (환경 변수에서 복사)"
    return
  fi

  if [[ ! -f "$ENV_EXAMPLE" ]]; then
    cat > "$ENV_EXAMPLE" <<'EOF'
# https://aistudio.google.com/app/api-keys
GEMINI_API_KEY=your_api_key_here
EOF
  fi

  echo "Gemini API 키를 입력하세요. (Enter = 나중에 .env에 직접 입력)"
  read -rsp "GEMINI_API_KEY: " api_key
  echo

  if [[ -n "$api_key" ]]; then
    printf 'GEMINI_API_KEY=%s\n' "$api_key" > "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    echo ".env 파일을 생성했습니다."
  else
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    echo ".env 템플릿을 생성했습니다. 키를 입력한 뒤 다시 실행하세요."
    echo "  $ENV_FILE"
  fi
}

setup_launchd() {
  step "launchd 설정"

  if [[ "$REGISTER_LAUNCHD" == "no" ]]; then
    echo "launchd 등록 건너뜀 (--no-launchd)"
    return
  fi

  if [[ ! -f "$ENV_FILE" ]] || ! grep -q '^GEMINI_API_KEY=.' "$ENV_FILE" 2>/dev/null || grep -q 'your_api_key_here' "$ENV_FILE" 2>/dev/null; then
    echo "GEMINI_API_KEY가 .env에 없습니다. launchd 등록은 건너뜁니다."
    echo "  $ENV_FILE 에 키를 입력한 뒤 ./launchd/install_launchd.sh 를 실행하세요."
    return
  fi

  MOBILE_NEWS_VENV="$VENV_DIR" "$PROJECT_DIR/launchd/install_launchd.sh"

  if [[ "$REGISTER_LAUNCHD" == "yes" ]]; then
    answer="y"
  else
    read -rp "launchd에 등록할까요? (매일 오전 9시 실행) [y/N]: " answer
  fi

  if [[ ! "$answer" =~ ^[Yy]$ ]]; then
    echo "plist만 생성했습니다. 나중에 등록하려면:"
    echo "  launchctl bootstrap gui/\$(id -u) ~/Library/LaunchAgents/com.news.daily.plist"
    return
  fi

  local plist="$HOME/Library/LaunchAgents/com.news.daily.plist"
  launchctl bootout "gui/$(id -u)" "$plist" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$plist"
  echo "launchd 등록 완료"
  echo "즉시 테스트: launchctl start com.news.daily"
}

print_summary() {
  step "설정 완료"
  cat <<EOF
다음 명령으로 실행할 수 있습니다:

  cd "$PROJECT_DIR"
  ./run.sh

알림만 테스트:

  ./run.sh test_notification.py

수동 실행 전 .env 확인:

  $ENV_FILE

launchd 상태 확인:

  launchctl list | grep com.news.daily
  tail -f /tmp/mobile-news.log
EOF
}

main() {
  echo "모바일 개발자 뉴스 요약 — 초기 설정"
  ensure_executable
  ensure_brew_deps
  ensure_python
  setup_herald_permission
  setup_venv
  setup_env_file
  setup_launchd
  print_summary
}

main
