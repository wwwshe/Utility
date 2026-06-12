# Utility

macOS용 유틸리티 모음 저장소입니다.

## 프로젝트

| 프로젝트 | 설명 |
|----------|------|
| [mobile-news](./mobile-news/) | Gemini API로 Apple / Flutter / Android 개발자 뉴스를 수집·요약하고, herald 알림으로 HTML 리포트를 전달 |
| [mac-cleanup](./mac-cleanup/) | 디스크 여유 공간이 5GB 이하일 때 캐시·Xcode 구버전 파일을 자동 정리하는 launchd 스케줄 |
| [compress](./compress/) | 폴더 내 PNG를 pngquant로 일괄 압축 |
| [resize](./resize/) | 폴더 내 PNG를 지정 해상도로 일괄 리사이즈 |

## 빠른 시작 (mobile-news)

```bash
git clone https://github.com/wwwshe/Utility.git
cd Utility/mobile-news
./setup.sh
./run.sh
```

자세한 설치·실행·릴리스 방법은 [mobile-news/README.md](./mobile-news/README.md)를 참고하세요.

## 빠른 시작 (mac-cleanup)

```bash
git clone https://github.com/wwwshe/Utility.git
cd Utility/mac-cleanup
./setup.sh
```

자세한 내용은 [mac-cleanup/README.md](./mac-cleanup/README.md)를 참고하세요.

## 빠른 시작 (compress / resize)

PNG 파일을 각 폴더에 넣고 스크립트를 실행한다.

```bash
# 압축
cd Utility/compress
brew install pngquant   # 최초 1회
bash compress_png.sh

# 리사이즈
cd Utility/resize
bash resize_png.sh 1024 768
```

자세한 내용은 [compress/README.md](./compress/README.md), [resize/README.md](./resize/README.md)를 참고하세요.

## 저장소 구조

```
Utility/
├── README.md
├── mobile-news/
│   ├── setup.sh          # 초기 설정
│   ├── run.sh            # 실행
│   ├── release.sh        # 릴리스 패키지 생성
│   ├── daily_news.py     # 메인 스크립트
│   └── README.md         # 상세 문서
├── mac-cleanup/
│   ├── setup.sh                          # 설치 스크립트
│   ├── mac-cleanup.sh                    # 정리 스크립트
│   ├── com.junwook.mac-cleanup.plist     # launchd 스케줄 설정
│   └── README.md                         # 상세 문서
├── compress/
│   ├── compress_png.sh                   # PNG 압축
│   └── README.md
└── resize/
    ├── resize_png.sh                     # PNG 리사이즈
    └── README.md
```

## Release

[mobile-news Release](https://github.com/wwwshe/Utility/releases)에서 설치 파일만 받을 수도 있습니다.

```bash
curl -L -o mobile-news.zip \
  https://github.com/wwwshe/Utility/releases/download/v1.0.0/mobile-news-1.0.0.zip
unzip mobile-news.zip
cd mobile-news
./setup.sh
```

## 요구 사항

- macOS
- Python 3
- [Homebrew](https://brew.sh/) (선택, `setup.sh`에서 의존성 설치 시 사용)
