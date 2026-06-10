#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$PROJECT_DIR/dist"
REPO_ROOT="$(git -C "$PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$PROJECT_DIR")"
VERSION=""
PUBLISH=0

usage() {
  cat <<EOF
사용법: ./release.sh --version <v1.0.0> [옵션]

옵션:
  -v, --version VER   릴리스 버전 (예: v1.0.0)
  --publish           GitHub Release 생성 및 업로드 (gh CLI 필요)
  -h, --help          도움말

예시:
  ./release.sh --version v1.0.0
  ./release.sh --version v1.0.0 --publish
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -v|--version)
      VERSION="$2"
      shift 2
      ;;
    --publish)
      PUBLISH=1
      shift
      ;;
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
done

if [[ -z "$VERSION" ]]; then
  echo "버전이 필요합니다. 예: ./release.sh --version v1.0.0" >&2
  exit 1
fi

if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "버전 형식은 vMAJOR.MINOR.PATCH 여야 합니다. (예: v1.0.0)" >&2
  exit 1
fi

VERSION_TAG="$VERSION"
ARCHIVE_BASE="mobile-news-${VERSION#v}"
STAGING_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/mobile-news-release.XXXXXX")"
STAGING_DIR="$STAGING_ROOT/mobile-news"
ZIP_PATH="$DIST_DIR/${ARCHIVE_BASE}.zip"
TAR_PATH="$DIST_DIR/${ARCHIVE_BASE}.tar.gz"
CHECKSUM_PATH="$DIST_DIR/${ARCHIVE_BASE}.sha256"

cleanup() {
  rm -rf "$STAGING_ROOT"
}
trap cleanup EXIT

step() {
  echo
  echo "==> $1"
}

step "릴리스 패키지 생성: $VERSION_TAG"

mkdir -p "$DIST_DIR" "$STAGING_DIR"

rsync -a \
  --exclude '.venv/' \
  --exclude '.env' \
  --exclude 'dev_news_*.html' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'dist/' \
  --exclude '.DS_Store' \
  "$PROJECT_DIR/" "$STAGING_DIR/"

(
  cd "$STAGING_ROOT"
  zip -r -q "$ZIP_PATH" mobile-news
  tar -czf "$TAR_PATH" mobile-news
)

if command -v shasum >/dev/null 2>&1; then
  (
    cd "$DIST_DIR"
    shasum -a 256 "$(basename "$ZIP_PATH")" "$(basename "$TAR_PATH")" > "$(basename "$CHECKSUM_PATH")"
  )
fi

echo "생성됨:"
echo "  $ZIP_PATH"
echo "  $TAR_PATH"
if [[ -f "$CHECKSUM_PATH" ]]; then
  echo "  $CHECKSUM_PATH"
fi

if [[ "$PUBLISH" -eq 1 ]]; then
  step "GitHub Release 업로드"

  if ! command -v gh >/dev/null 2>&1; then
    echo "gh CLI가 필요합니다. (brew install gh)" >&2
    exit 1
  fi

  if [[ -n "$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null)" ]]; then
    echo "커밋되지 않은 변경이 있습니다. Release 전에 커밋하세요." >&2
    exit 1
  fi

  if git -C "$REPO_ROOT" rev-parse "$VERSION_TAG" >/dev/null 2>&1; then
    echo "태그가 이미 있습니다: $VERSION_TAG"
  else
    git -C "$REPO_ROOT" tag -a "$VERSION_TAG" -m "mobile-news $VERSION_TAG"
    echo "태그 생성: $VERSION_TAG"
  fi

  git -C "$REPO_ROOT" push origin "$VERSION_TAG"

  gh release create "$VERSION_TAG" \
    "$ZIP_PATH" \
    "$TAR_PATH" \
    ${CHECKSUM_PATH:+"$CHECKSUM_PATH"} \
    --repo "$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo wwwshe/Utility)" \
    --title "mobile-news ${VERSION#v}" \
    --notes "$(cat <<EOF
## mobile-news ${VERSION#v}

설치:

\`\`\`bash
curl -L -o mobile-news.zip \\
  https://github.com/wwwshe/Utility/releases/download/${VERSION_TAG}/${ARCHIVE_BASE}.zip
unzip mobile-news.zip
cd mobile-news
./setup.sh
\`\`\`
EOF
)"

  echo "GitHub Release 업로드 완료: $VERSION_TAG"
else
  echo
  echo "GitHub에 올리려면:"
  echo "  ./release.sh --version $VERSION_TAG --publish"
  echo
  echo "또는 Release 페이지에서 수동 업로드:"
  echo "  $ZIP_PATH"
  echo "  $TAR_PATH"
fi
