# Utility

macOS용 유틸리티 모음 저장소입니다.

## 프로젝트

| 프로젝트 | 설명 |
|----------|------|
| [mobile-news](./mobile-news/) | Gemini API로 Apple / Flutter / Android 개발자 뉴스를 수집·요약하고, herald 알림으로 HTML 리포트를 전달 |

## 빠른 시작 (mobile-news)

```bash
git clone https://github.com/wwwshe/Utility.git
cd Utility/mobile-news
./setup.sh
./run.sh
```

자세한 설치·실행·릴리스 방법은 [mobile-news/README.md](./mobile-news/README.md)를 참고하세요.

## 저장소 구조

```
Utility/
├── README.md
└── mobile-news/
    ├── setup.sh          # 초기 설정
    ├── run.sh            # 실행
    ├── release.sh        # 릴리스 패키지 생성
    ├── daily_news.py     # 메인 스크립트
    └── README.md         # 상세 문서
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
