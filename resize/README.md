# resize

스크립트가 있는 폴더의 PNG 이미지를 지정한 픽셀 크기로 일괄 리사이즈한다.  
macOS 기본 도구 `sips`를 사용하며, 원본 파일을 덮어쓴다.

## 파일 구조

```
resize/
├── resize_png.sh    # 리사이즈 스크립트
└── README.md
```

## 요구 사항

- macOS (`sips` 내장)

## 사용법

리사이즈할 PNG 파일을 `resize/` 폴더에 넣은 뒤, 목표 너비·높이를 인자로 넘긴다.

```bash
cd resize
bash resize_png.sh <width> <height>
```

예시:

```bash
bash resize_png.sh 1024 768
```

## 동작

- `resize/` 폴더 안의 `*.png` 파일을 대상으로 한다.
- `width`, `height`는 양의 정수여야 한다.
- 파일별 원본·변경 후 해상도를 출력한다.

## 주의

- **원본이 덮어쓰기**되므로 필요하면 미리 백업한다.
- 비율을 유지하지 않고 지정한 크기로 맞춘다.
- PNG가 없으면 처리할 파일이 없다는 메시지만 출력된다.
