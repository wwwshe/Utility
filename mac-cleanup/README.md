# mac-cleanup

맥북 디스크 용량 자동 정리 스크립트.  
매일 오후 4시에 여유 공간을 체크하고, **5GB 이하일 때만** 자동으로 정리를 실행한다.

## 파일 구조

```
mac-cleanup/
├── mac-cleanup.sh                   # 정리 스크립트
├── com.junwook.mac-cleanup.plist    # launchd 스케줄 설정
├── setup.sh                         # 설치 스크립트
└── README.md
```

## 설치

```bash
bash [이 폴더 경로]/setup.sh
```

설치 후 생성되는 파일:
- `~/mac-cleanup.sh` — 실행 스크립트
- `~/Library/LaunchAgents/com.junwook.mac-cleanup.plist` — launchd 등록
- `~/mac-cleanup.log` — 실행 로그

## 정리 항목

### ~/Library/Caches
- Google (Chrome 캐시)
- CocoaPods
- org.swift.swiftpm (Swift Package Manager)
- Homebrew
- node-gyp
- ms-playwright
- pip
- SiriTTS
- com.anthropic.claudefordesktop.ShipIt (Claude 앱 업데이트 캐시)
- com.todesktop.230313mzl4w4u92.ShipIt
- typescript

### Gradle
- `$GRADLE_USER_HOME/caches` (외장 경로 자동 감지)
- 기본값: `~/.gradle/caches`

### npm
- `~/.npm/_npx` (npx 임시 실행 캐시)

### CocoaPods
- `~/.cocoapods/repos` (스펙 저장소 캐시)

### Xcode
- `~/Library/Developer/Xcode/DerivedData` (빌드 캐시, 다음 빌드 시 재생성)
- `~/Library/Developer/Xcode/Archives` — 앱별 구버전 아카이브 삭제, 최신 1개만 유지
- `~/Library/Developer/Xcode/iOS DeviceSupport` — 기기별 구버전 삭제, 최신만 유지
- `~/Library/Logs/CoreSimulator` (시뮬레이터 로그)
- `~/Library/Developer/Xcode/iOS Device Logs` (실기기 연결 로그)

> **iPhone 12 (iPhone13,2)** DeviceSupport는 삭제하지 않음.  
> 실기기 연결 시 Xcode가 자동으로 재생성하므로 제외.

## 수동 실행

지금 바로 실행하고 싶을 때:

```bash
bash ~/mac-cleanup.sh
```

## 로그 확인

```bash
cat ~/mac-cleanup.log
```

## 외장하드 연동

npm, Gradle 캐시는 외장하드(`/Volumes/500G`)로 이동된 상태.  
외장하드가 연결되지 않은 상태에서는 빌드가 실패할 수 있으니 주의.

| 도구 | 캐시 경로 |
|------|----------|
| npm | `/Volumes/500G/.npm` |
| Gradle | `/Volumes/500G/.gradle` |

## 제거

```bash
launchctl unload ~/Library/LaunchAgents/com.junwook.mac-cleanup.plist
rm ~/Library/LaunchAgents/com.junwook.mac-cleanup.plist
rm ~/mac-cleanup.sh
rm ~/mac-cleanup.log
```
