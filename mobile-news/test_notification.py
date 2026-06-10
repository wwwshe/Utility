#!/usr/bin/env python3
"""생성된 HTML 리포트로 herald 알림만 테스트합니다."""

import argparse
import glob
import os
import shutil
import subprocess


def find_latest_html(directory):
    pattern = os.path.join(directory, "dev_news_*.html")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def send_notification(title, message, filepath):
    abs_filepath = os.path.abspath(filepath)
    herald = shutil.which("herald")

    if not herald:
        print("⚠ herald가 설치되어 있지 않습니다.")
        print("   brew install mdsakalu/tap/herald")
        return 1

    if not os.path.isfile(abs_filepath):
        print(f"⚠ HTML 파일을 찾을 수 없습니다: {abs_filepath}")
        return 1

    result = subprocess.run(
        [
            herald,
            "--title",
            title,
            "--message",
            message,
            "--on-click",
            f"open:{abs_filepath}",
            "--sound",
            "default",
            "--timeout",
            "0",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("✅ 알림 전송 완료")
        print(f"   대상 파일: {abs_filepath}")
        print("   알림을 클릭하면 리포트가 열립니다.")
        return 0

    error = result.stderr.strip() or result.stdout.strip() or "알 수 없는 오류"
    print(f"⚠ 알림 실패: {error}")
    print("   open /opt/homebrew/opt/herald/Herald.app 로 권한을 다시 확인해 주세요.")
    return 1


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="HTML 리포트 알림만 테스트합니다.")
    parser.add_argument(
        "html",
        nargs="?",
        help="알림에 연결할 HTML 파일 경로 (생략 시 최신 dev_news_*.html)",
    )
    parser.add_argument("--title", default="📰 모바일 개발자 뉴스 요약 완료")
    parser.add_argument("--message", default="알림을 클릭하면 리포트가 열립니다.")
    args = parser.parse_args()

    html_path = args.html
    if not html_path:
        html_path = find_latest_html(script_dir)
        if not html_path:
            print("⚠ dev_news_*.html 파일이 없습니다.")
            print("   먼저 daily_news.py를 실행하거나 HTML 경로를 직접 지정해 주세요.")
            return 1
        print(f"📄 최신 리포트 사용: {html_path}")

    return send_notification(args.title, args.message, html_path)


if __name__ == "__main__":
    raise SystemExit(main())
