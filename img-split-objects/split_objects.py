"""
split_objects.py
────────────────
이미지 1장 → 투명 배경 기준으로 오브젝트를 개별 PNG 파일로 저장

• RGBA 이미지: 알파 채널로 오브젝트 분리 (rembg 불필요)
• RGB 이미지:  흰색/단색 배경을 투명으로 변환 후 분리

사용법:
    python split_objects.py <이미지경로> [옵션]

옵션:
    --out_dir     출력 폴더 (기본: ./output)
    --min_size    무시할 최소 픽셀 수 (기본: 1000)
    --bg_color    RGB 배경 이미지일 때 배경 색상 r,g,b (기본: 255,255,255)
    --bg_thresh   배경 판정 임계값 (기본: 30)

예시:
    python split_objects.py icons.png
    python split_objects.py icons.png --out_dir results
    python split_objects.py icons.png --bg_color 0,0,0 --bg_thresh 20
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def load_as_rgba(image_path: str, bg_color: tuple, bg_thresh: int) -> Image.Image:
    """이미지를 RGBA로 로드. RGB면 배경색을 투명으로 변환."""
    img = Image.open(image_path)

    if img.mode == "RGBA":
        print(f"✅  RGBA 이미지 감지 — 알파 채널로 배경 구분")
        return img

    img = img.convert("RGBA")
    arr = np.array(img)
    rgb = arr[:, :, :3].astype(int)
    bg = np.array(bg_color, dtype=int)

    # 배경과 가까운 픽셀 투명 처리
    dist = np.linalg.norm(rgb - bg, axis=2)
    bg_mask = dist < bg_thresh
    arr[bg_mask, 3] = 0

    print(f"✅  RGB 이미지 — 배경색 {bg_color} 기준으로 투명 변환")
    return Image.fromarray(arr, "RGBA")


def split_objects(img: Image.Image, min_size: int) -> list[Image.Image]:
    """알파 채널 기반으로 연결된 오브젝트를 개별 이미지로 분리."""
    arr = np.array(img)
    alpha = arr[:, :, 3]
    fg_mask = alpha > 128

    labeled, n = ndimage.label(fg_mask)
    print(f"🔍  감지된 컴포넌트: {n}개")

    # 크기 순 정렬
    sizes = [(label_id, (labeled == label_id).sum()) for label_id in range(1, n + 1)]
    sizes.sort(key=lambda x: -x[1])

    objects = []
    skipped = 0

    for label_id, size in sizes:
        if size < min_size:
            skipped += 1
            continue

        mask = labeled == label_id
        rows = np.where(np.any(mask, axis=1))[0]
        cols = np.where(np.any(mask, axis=0))[0]
        y0, y1 = rows[0], rows[-1] + 1
        x0, x1 = cols[0], cols[-1] + 1

        cropped = arr[y0:y1, x0:x1].copy()
        crop_mask = mask[y0:y1, x0:x1]
        cropped[~crop_mask, 3] = 0  # 다른 오브젝트 픽셀 투명 처리

        objects.append(Image.fromarray(cropped, "RGBA"))

    if skipped:
        print(f"⚠️   {skipped}개 컴포넌트는 min_size({min_size}) 미만으로 제외")

    return objects


def save_objects(objects: list[Image.Image], out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, obj in enumerate(objects, 1):
        path = out_dir / f"{stem}_{i:02d}.png"
        obj.save(path)
        print(f"  💾  {path}  ({obj.width}x{obj.height})")


def main():
    parser = argparse.ArgumentParser(
        description="이미지에서 오브젝트를 개별 PNG로 분리 저장"
    )
    parser.add_argument("image", help="입력 이미지 경로")
    parser.add_argument("--out_dir", default="output", help="출력 폴더 (기본: ./output)")
    parser.add_argument("--min_size", type=int, default=1000, help="최소 픽셀 수 (기본: 1000)")
    parser.add_argument("--bg_color", default="255,255,255", help="RGB 배경 색상 (기본: 255,255,255)")
    parser.add_argument("--bg_thresh", type=int, default=30, help="배경 판정 임계값 (기본: 30)")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        sys.exit(f"❌  파일을 찾을 수 없습니다: {image_path}")

    try:
        bg_color = tuple(int(x) for x in args.bg_color.split(","))
        assert len(bg_color) == 3
    except Exception:
        sys.exit("❌  --bg_color 형식 오류. 예: --bg_color 255,255,255")

    img = load_as_rgba(str(image_path), bg_color, args.bg_thresh)

    objects = split_objects(img, args.min_size)

    if not objects:
        sys.exit("⚠️  분리된 오브젝트가 없습니다. --min_size를 낮춰보세요.")

    print(f"\n📦  {len(objects)}개 오브젝트 저장 중...")
    save_objects(objects, Path(args.out_dir), image_path.stem)
    print(f"\n✅  완료! → {Path(args.out_dir).resolve()}")


if __name__ == "__main__":
    main()
