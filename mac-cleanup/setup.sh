#!/bin/bash

# -----------------------------------------------
# mac-cleanup setup.sh
# 매일 오후 4시 디스크 용량 자동 정리 설치 스크립트
# -----------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_SRC="$SCRIPT_DIR/mac-cleanup.sh"
PLIST_SRC="$SCRIPT_DIR/com.junwook.mac-cleanup.plist"

SCRIPT_DST=~/mac-cleanup.sh
PLIST_DST=~/Library/LaunchAgents/com.junwook.mac-cleanup.plist
LOG_FILE=~/mac-cleanup.log

echo "🔧 mac-cleanup 설치 시작..."

# 1. 스크립트 복사 및 실행 권한 부여
cp "$SCRIPT_SRC" "$SCRIPT_DST"
chmod +x "$SCRIPT_DST"
echo "✅ 정리 스크립트 설치 완료: $SCRIPT_DST"

# 2. LaunchAgents 폴더 확인
mkdir -p ~/Library/LaunchAgents

# 3. 기존 plist 언로드 (재설치 시 충돌 방지)
if launchctl list | grep -q "com.junwook.mac-cleanup"; then
  launchctl unload "$PLIST_DST" 2>/dev/null
  echo "♻️  기존 스케줄 제거"
fi

# 4. plist 복사 및 등록
cp "$PLIST_SRC" "$PLIST_DST"
launchctl load "$PLIST_DST"
echo "✅ 스케줄 등록 완료: 매일 오후 4시 자동 실행"

# 5. 로그 파일 초기화
touch "$LOG_FILE"
echo "📋 로그 파일: $LOG_FILE"

echo ""
echo "🎉 설치 완료!"
echo "   - 매일 오후 4시에 디스크 여유 공간을 체크해요"
echo "   - 5GB 이하일 때만 자동 정리가 실행돼요"
echo "   - 로그 확인: cat ~/mac-cleanup.log"
echo ""
echo "   지금 바로 테스트하려면:"
echo "   bash ~/mac-cleanup.sh"
