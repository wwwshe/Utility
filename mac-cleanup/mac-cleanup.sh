#!/bin/bash

LOG_PREFIX="$(date '+%Y-%m-%d %H:%M:%S')"

# 여유 공간 확인 (GB 단위)
AVAIL=$(df -g / | awk 'NR==2 {print $4}')

if [ "$AVAIL" -gt 5 ]; then
  echo "$LOG_PREFIX: 여유 공간 ${AVAIL}GB — 정리 불필요"
  exit 0
fi

echo "$LOG_PREFIX: 여유 공간 ${AVAIL}GB — 정리 시작"

# ── ~/Library/Caches 정리 ──────────────────────────
CACHES=(
  "Google"
  "CocoaPods"
  "org.swift.swiftpm"
  "Homebrew"
  "node-gyp"
  "ms-playwright"
  "pip"
  "SiriTTS"
  "com.anthropic.claudefordesktop.ShipIt"
  "com.todesktop.230313mzl4w4u92.ShipIt"
  "typescript"
)

for folder in "${CACHES[@]}"; do
  TARGET=~/Library/Caches/"$folder"
  if [ -e "$TARGET" ]; then
    rm -rf "$TARGET"
    echo "$LOG_PREFIX: 삭제 — Caches/$folder"
  fi
done

# ── Gradle 빌드 캐시 정리 ──────────────────────────
# GRADLE_USER_HOME이 외장이면 외장 경로, 아니면 기본 경로
GRADLE_HOME="${GRADLE_USER_HOME:-$HOME/.gradle}"
if [ -d "$GRADLE_HOME/caches" ]; then
  rm -rf "$GRADLE_HOME/caches"
  echo "$LOG_PREFIX: 삭제 — gradle/caches"
fi

# ── npm npx 임시 캐시 정리 ────────────────────────
if [ -d ~/.npm/_npx ]; then
  rm -rf ~/.npm/_npx
  echo "$LOG_PREFIX: 삭제 — .npm/_npx"
fi

# ── CocoaPods 스펙 저장소 캐시 ────────────────────
if [ -d ~/.cocoapods/repos ]; then
  rm -rf ~/.cocoapods/repos
  echo "$LOG_PREFIX: 삭제 — .cocoapods/repos"
fi

# ── Xcode DerivedData 정리 ────────────────────────
rm -rf ~/Library/Developer/Xcode/DerivedData/*
echo "$LOG_PREFIX: 삭제 — DerivedData"

# ── Xcode 로그 정리 ───────────────────────────────
if [ -d ~/Library/Logs/CoreSimulator ]; then
  rm -rf ~/Library/Logs/CoreSimulator/*
  echo "$LOG_PREFIX: 삭제 — Logs/CoreSimulator"
fi

if [ -d ~/Library/Developer/Xcode/iOS\ Device\ Logs ]; then
  rm -rf ~/Library/Developer/Xcode/iOS\ Device\ Logs/*
  echo "$LOG_PREFIX: 삭제 — Xcode/iOS Device Logs"
fi

# ── Xcode DeviceSupport 구버전 정리 (iPhone13,2 제외) ──
DEVSUPP=~/Library/Developer/Xcode/iOS\ DeviceSupport

# 모델별 그룹화 후 최신 버전 제외하고 삭제
ls "$DEVSUPP" 2>/dev/null | grep -v "^iPhone13,2" | awk '{print $1}' | sort -u | while read model; do
  find "$DEVSUPP" -maxdepth 1 -type d -name "$model *" | sort | head -n -1 | while read old_dir; do
    rm -rf "$old_dir"
    echo "$LOG_PREFIX: 삭제 — iOS DeviceSupport/$(basename "$old_dir")"
  done
done

# ── Xcode Archives 구버전 정리 (앱별 최신 1개 유지) ──
ARCHIVES=~/Library/Developer/Xcode/Archives

if [ -d "$ARCHIVES" ]; then
  KEEP_LIST=$(mktemp)
  find "$ARCHIVES" -name "*.xcarchive" -type d | sort | while read -r archive; do
    # "AppName 6-15-24, 3.45 PM.xcarchive" → 앱 이름 추출
    app_name=$(basename "$archive" .xcarchive | sed 's/ [0-9][0-9]*-[0-9][0-9]*-[0-9][0-9]*,.*//')
    echo "$app_name|$archive"
  done | awk -F'|' '{latest[$1]=$2} END{for (a in latest) print latest[a]}' > "$KEEP_LIST"

  find "$ARCHIVES" -name "*.xcarchive" -type d | while read -r archive; do
    if ! grep -Fxq "$archive" "$KEEP_LIST"; then
      rm -rf "$archive"
      rel_path="${archive#$ARCHIVES/}"
      echo "$LOG_PREFIX: 삭제 — Archives/$rel_path"
    fi
  done

  rm -f "$KEEP_LIST"
  find "$ARCHIVES" -mindepth 1 -maxdepth 1 -type d -empty -delete 2>/dev/null
fi

# 정리 후 여유 공간 확인
AFTER=$(df -g / | awk 'NR==2 {print $4}')
echo "$LOG_PREFIX: 정리 완료 — 여유 공간 ${AVAIL}GB → ${AFTER}GB"
