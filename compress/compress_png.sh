#!/bin/bash

# PNG 이미지 pngquant 압축 스크립트
# 실행 방법: bash compress_png.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "📦 pngquant 압축 시작..."
echo "📁 폴더: $SCRIPT_DIR"
echo ""

# 압축 전 총 크기
BEFORE=$(du -sh "$SCRIPT_DIR"/*.png 2>/dev/null | awk '{sum += $1} END {print sum}')

count=0
for file in "$SCRIPT_DIR"/*.png; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        before_size=$(wc -c < "$file")

        # pngquant 적용 (원본 덮어쓰기)
        pngquant --quality=65-85 --speed 1 --force --output "$file" "$file"

        after_size=$(wc -c < "$file")
        saved=$(( (before_size - after_size) * 100 / before_size ))

        echo "✅ $filename: $(echo "scale=1; $before_size/1024" | bc)KB → $(echo "scale=1; $after_size/1024" | bc)KB (${saved}% 절약)"
        count=$((count + 1))
    fi
done

echo ""
echo "🎉 완료! 총 ${count}개 파일 압축됨"
