#!/bin/bash

# PNG 이미지 리사이즈 스크립트
# 실행 방법: bash resize_png.sh <width> <height>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 인자 확인
if [ $# -ne 2 ]; then
    echo "❌ 사용법: bash resize_png.sh <width> <height>"
    echo "   예시:   bash resize_png.sh 1024 768"
    exit 1
fi

TARGET_W=$1
TARGET_H=$2

# 숫자 유효성 검사
if ! [[ "$TARGET_W" =~ ^[0-9]+$ ]] || ! [[ "$TARGET_H" =~ ^[0-9]+$ ]]; then
    echo "❌ width, height는 양의 정수여야 합니다."
    exit 1
fi

echo "🖼️  PNG 리사이즈 시작..."
echo "📁 폴더: $SCRIPT_DIR"
echo "📐 목표 크기: ${TARGET_W} x ${TARGET_H}"
echo ""

count=0
fail=0

for file in "$SCRIPT_DIR"/*.png; do
    [ -f "$file" ] || continue

    filename=$(basename "$file")

    # 원본 크기 확인 (sips)
    orig_w=$(sips -g pixelWidth  "$file" 2>/dev/null | awk '/pixelWidth/{print $2}')
    orig_h=$(sips -g pixelHeight "$file" 2>/dev/null | awk '/pixelHeight/{print $2}')

    # 리사이즈 (원본 덮어쓰기)
    if sips -z "$TARGET_H" "$TARGET_W" "$file" --out "$file" > /dev/null 2>&1; then
        echo "✅ $filename: ${orig_w}x${orig_h} → ${TARGET_W}x${TARGET_H}"
        count=$((count + 1))
    else
        echo "❌ $filename: 실패"
        fail=$((fail + 1))
    fi
done

if [ $count -eq 0 ] && [ $fail -eq 0 ]; then
    echo "⚠️  처리할 PNG 파일이 없습니다."
    exit 0
fi

echo ""
echo "🎉 완료! 성공 ${count}개 / 실패 ${fail}개"
