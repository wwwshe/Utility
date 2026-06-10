# 모바일 개발자 뉴스 요약 (Gemini API)

Apple Developer, Flutter Medium, Android Developers RSS 피드를 수집하고, **Gemini API**로 한국어 요약한 뒤 HTML 리포트를 생성하는 macOS용 유틸리티입니다.

실행이 끝나면 **macOS 알림**이 오고, 알림을 클릭하면 생성된 HTML 파일이 브라우저에서 열립니다.

## 수집 소스

| 플랫폼 | RSS |
|--------|-----|
| Apple | https://developer.apple.com/news/rss/news.rss |
| Flutter | https://medium.com/feed/flutter |
| Android | https://android-developers.googleblog.com/feeds/posts/default |

## 프로젝트 받기

아래 방법 중 하나로 `mobile-news` 폴더를 준비한 뒤 `./setup.sh`를 실행합니다.

| 방법 | 설명 |
|------|------|
| git clone | 저장소 전체 받기 (권장) |
| GitHub Release | 릴리스에 첨부된 zip/tar.gz만 다운로드 |
| ZIP 다운로드 | **Code → Download ZIP** 후 압축 해제 |
| 폴더 복사 | USB, AirDrop 등으로 `mobile-news` 폴더 전달 |

### git clone (권장)

```bash
git clone https://github.com/wwwshe/Utility.git
cd Utility/mobile-news
./setup.sh
./run.sh
```

### GitHub Release에서 받기

```bash
curl -L -o mobile-news.zip \
  https://github.com/wwwshe/Utility/releases/download/v1.0.0/mobile-news.zip
unzip mobile-news.zip
cd mobile-news
./setup.sh
```

### ZIP으로 받기

1. https://github.com/wwwshe/Utility 에서 **Code → Download ZIP**
2. 압축 해제 후 `Utility/mobile-news` 로 이동
3. `./setup.sh` 실행

## 빠른 시작

프로젝트를 받은 뒤:

```bash
cd /path/to/mobile-news
./setup.sh
./run.sh
```

`setup.sh` 한 번으로 아래를 처리합니다.

1. 실행 권한 설정 (`setup.sh`, `run.sh`, `install_launchd.sh`)
2. Homebrew로 `python3`, `herald` 설치 (없을 때)
3. Herald 알림 권한 요청 (`Herald.app` 실행)
4. Python 가상환경 생성 + 패키지 설치 (`.venv`)
5. `.env` 파일 생성 (Gemini API 키)
6. launchd plist 생성 + 등록 (선택)

### setup.sh 옵션

```bash
./setup.sh              # 대화형 (launchd 등록 여부 질문)
./setup.sh --yes        # 질문 없이 전부 진행
./setup.sh --no-launchd # launchd 등록 건너뛰기
./setup.sh --skip-brew  # brew 설치 단계 건너뛰기
```

### 가상환경 경로 변경

기본: `프로젝트/.venv`

```bash
export MOBILE_NEWS_VENV="$HOME/Python-Venv/mobile-news"
./setup.sh
```

### Gemini API 키

setup 중 입력하거나, `.env` 파일에 직접 작성합니다.

```bash
# .env
GEMINI_API_KEY=발급받은_API_키
```

발급: [Google AI Studio](https://aistudio.google.com/app/api-keys)

## 실행

```bash
./run.sh                          # 뉴스 수집 + 요약 + 알림
./run.sh test_notification.py     # 알림만 테스트
```

## Herald 알림 권한

setup 시 `Herald.app`이 자동 실행됩니다. 팝업이 뜨면 **허용**을 눌러 주세요.

수동으로 다시 요청:

```bash
open /opt/homebrew/opt/herald/Herald.app
```

권한 초기화:

```bash
tccutil reset Notifications com.herald.cli
open /opt/homebrew/opt/herald/Herald.app
```

## launchd (매일 오전 9시)

`setup.sh`에서 등록하거나, 나중에 수동으로:

```bash
./launchd/install_launchd.sh
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.news.daily.plist
launchctl start com.news.daily
```

해제:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.news.daily.plist
rm ~/Library/LaunchAgents/com.news.daily.plist
```

로그: `/tmp/mobile-news.log`, `/tmp/mobile-news.error.log`

## 릴리스 만들기 (개발자용)

GitHub Release에 올릴 zip/tar.gz를 생성합니다.  
`.env`, `.venv`, `dev_news_*.html` 등은 패키지에서 제외됩니다.

```bash
cd mobile-news

# 패키지만 생성 → dist/mobile-news-1.0.0.zip
./release.sh --version v1.0.0

# GitHub Release까지 업로드 (gh CLI, git tag push 필요)
./release.sh --version v1.0.0 --publish
```

`--publish` 사용 전:

```bash
brew install gh
gh auth login
git add . && git commit -m "..."
```

## 프로젝트 구조

```
mobile-news/
├── setup.sh                       # 전체 초기 설정
├── run.sh                         # 실행 래퍼 (.env 자동 로드)
├── release.sh                     # 릴리스 패키지 생성
├── .env.example                   # API 키 템플릿
├── daily_news.py
├── test_notification.py
├── requirements.txt
├── launchd/
│   ├── com.news.daily.plist.template
│   └── install_launchd.sh
└── README.md
```

## 문제 해결

| 증상 | 확인 사항 |
|------|-----------|
| `가상환경이 없습니다` | `./setup.sh` 재실행 |
| `GEMINI_API_KEY가 없습니다` | `.env` 파일에 키 입력 |
| 알림이 오지 않음 | `open /opt/homebrew/opt/herald/Herald.app` 후 Herald 허용 |
| launchd 미등록 | `.env`에 API 키 입력 후 `./setup.sh` 또는 `install_launchd.sh` |
| 요약이 비어 있음 | 네트워크, Gemini API 키·할당량 확인 |

## 의존성

- `google-generativeai` — Gemini API
- `feedparser` — RSS 파싱
- `markdown` — 요약 텍스트 HTML 변환
