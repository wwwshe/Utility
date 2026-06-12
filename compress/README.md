# compress

스크립트가 있는 폴더의 PNG 이미지를 [pngquant](https://pngquant.org/)로 일괄 압축한다.  
원본 파일을 덮어쓴다.

## 파일 구조

```
compress/
├── compress_png.sh    # 압축 스크립트
└── README.md
```

## 요구 사항

- macOS
- [pngquant](https://pngquant.org/)

```bash
brew install pngquant
```

## 사용법

압축할 PNG 파일을 `compress/` 폴더에 넣은 뒤 실행한다.

```bash
cd compress
bash compress_png.sh
```

## 동작

- `compress/` 폴더 안의 `*.png` 파일을 대상으로 한다.
- `pngquant --quality=65-85 --speed 1` 옵션으로 압축한다.
- 파일별 압축 전·후 크기와 절약 비율을 출력한다.

## 주의

- **원본이 덮어쓰기**되므로 필요하면 미리 백업한다.
- PNG가 없으면 처리할 파일이 없다는 메시지만 출력된다.
