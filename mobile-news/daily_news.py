#!/usr/bin/env python3
"""Gemini API로 Apple / Flutter / Android 개발자 뉴스를 수집·요약해 HTML 리포트를 생성합니다."""

import feedparser
import google.generativeai as genai
from datetime import datetime
import os
import markdown
import shutil
import subprocess

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


def get_article_date(article):
    """기사 항목에서 published_parsed 또는 updated_parsed를 안전하게 가져옵니다."""
    if "published_parsed" in article and article.published_parsed:
        return article.published_parsed
    if "updated_parsed" in article and article.updated_parsed:
        return article.updated_parsed
    return None


def format_date_tuple(date_tuple):
    """날짜 튜플을 YYYY-MM-DD 형식의 문자열로 변환합니다."""
    if date_tuple and len(date_tuple) >= 3:
        try:
            return f"{date_tuple.tm_year}-{date_tuple.tm_mon:02d}-{date_tuple.tm_mday:02d}"
        except AttributeError:
            return "날짜 오류"
    return "날짜 없음"


def fetch_apple_news():
    feeds = ["https://developer.apple.com/news/rss/news.rss"]
    articles = []
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        articles.extend(feed.entries[:5])
    return articles


def fetch_flutter_news():
    flutter_feed_url = "https://medium.com/feed/flutter"
    feed = feedparser.parse(flutter_feed_url)
    return feed.entries[:5]


def fetch_android_news():
    android_feed_url = "https://android-developers.googleblog.com/feeds/posts/default"
    feed = feedparser.parse(android_feed_url)
    return feed.entries[:5]


def summarize_with_gemini(articles, title_prefix, prompt_instruction, link_class):
    """뉴스 종류에 관계없이 요약을 수행하고 링크를 삽입하는 범용 함수."""
    if not articles:
        return f"<p>현재 새로운 {title_prefix} 소식이 없습니다.</p>"

    model = genai.GenerativeModel("gemini-2.5-flash")
    title_to_link = {}

    article_text = ""
    for i, article in enumerate(articles[:15]):
        article_text += f"[{i}] 제목: {article.title}\n"
        article_text += f"링크: {article.link}\n"
        article_text += f"요약: {article.get('summary', '')[:200]}\n\n"
        title_to_link[f"제목:{article.title}"] = article.link

    prompt = f"""다음 {title_prefix} 뉴스들을 한국어로 요약해줘.
{prompt_instruction}

반드시 이 형식으로 답해줘:
### 기사 제목 (원문 제목을 그대로 사용)
2-3문장으로 요약 (개발에 미치는 영향 포함)

---

뉴스:
{article_text}"""

    response = model.generate_content(prompt)
    raw_text = response.text

    for key, link in title_to_link.items():
        original_title = key.split(":", 1)[1].strip()
        markdown_title = f"### {original_title}"
        html_link = (
            f'<h3><a href="{link}" target="_blank" class="{link_class}">'
            f"{original_title}</a></h3>"
        )
        raw_text = raw_text.replace(markdown_title, html_link)

    return markdown.markdown(raw_text)


def summarize_apple_with_gemini(articles):
    prompt_instruction = (
        "iOS 개발자 관점에서 중요한 뉴스를 우선 선별하고, "
        "WWDC, Xcode, Swift, App Store 관련 변경사항을 강조해줘."
    )
    return summarize_with_gemini(
        articles, "애플 개발자", prompt_instruction, "summary-link apple-link"
    )


def summarize_flutter_with_gemini(articles):
    prompt_instruction = (
        "모바일(iOS/Android) 개발자 관점에서 중요한 변경사항과 "
        "새로운 기능을 우선 선별해줘."
    )
    return summarize_with_gemini(
        articles, "Flutter", prompt_instruction, "summary-link flutter-link"
    )


def summarize_android_with_gemini(articles):
    prompt_instruction = (
        "Android 개발자 관점에서 중요한 뉴스를 우선 선별하고, "
        "Jetpack, Kotlin, Play Store 관련 변경사항을 강조해줘."
    )
    return summarize_with_gemini(
        articles, "Android 개발자", prompt_instruction, "summary-link android-link"
    )


def generate_html(
    apple_summary,
    flutter_summary,
    android_summary,
    apple_articles,
    flutter_articles,
    android_articles,
):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(
        script_dir, f"dev_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>모바일 개발자 뉴스 요약 - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: #fff;
            color: #1d1d1f;
        }}
        h1 {{
            color: #1d1d1f;
            font-size: 32px;
            font-weight: 600;
        }}
        .date {{
            color: #6e6e73;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .summary {{
            background: #f5f5f7;
            padding: 24px;
            border-radius: 12px;
            margin: 24px 0;
            line-height: 1.8;
        }}
        .summary h2 {{
            margin-top: 0;
            font-size: 24px;
            font-weight: 600;
            color: #1d1d1f;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .summary-link {{
            text-decoration: none;
            font-weight: 600;
        }}
        .apple-link {{ color: #0071e3; }}
        .flutter-link {{ color: #02569b; }}
        .android-link {{ color: #3ddc84; }}
        .summary-link:hover {{ text-decoration: underline; }}
        .summary p {{
            margin: 8px 0;
            line-height: 1.6;
        }}
        .articles {{ margin-top: 40px; }}
        .article {{
            margin: 16px 0;
            padding: 16px;
            background: #fafafa;
            border-radius: 8px;
            border: 1px solid #eee;
        }}
        .apple-article-link {{ color: #0071e3; text-decoration: none; }}
        .flutter-article-link {{ color: #02569b; text-decoration: none; }}
        .android-article-link {{ color: #3ddc84; text-decoration: none; }}
        .article h3 {{
            margin: 0 0 8px 0;
            font-size: 18px;
            font-weight: 500;
        }}
        .article a:hover {{ text-decoration: underline; }}
        .source {{
            color: #86868b;
            font-size: 12px;
            margin-top: 4px;
        }}
    </style>
</head>
<body>
    <h1>💻 모바일 개발자 뉴스 요약</h1>
    <p class="date">{datetime.now().strftime('%Y년 %m월 %d일 %A')}</p>

    <div class="summary apple-summary">
        <h2>🍎 Apple News 주요 소식</h2>
        {apple_summary}
    </div>

    <div class="summary flutter-summary">
        <h2>🐦 Flutter News 주요 소식</h2>
        {flutter_summary}
    </div>

    <div class="summary android-summary">
        <h2>🤖 Android News 주요 소식</h2>
        {android_summary}
    </div>

    <div class="articles">
        <h2>📑 전체 기사 목록</h2>

        <h3>🍎 Apple Developer News ({len(apple_articles)}개)</h3>
        {''.join(f'''
        <div class="article">
            <h3><a href="{article.link}" target="_blank" class="apple-article-link">{article.title}</a></h3>
            <div class="source">Apple News - {format_date_tuple(get_article_date(article))}</div>
        </div>
        ''' for article in apple_articles)}

        <h3>🐦 Flutter News ({len(flutter_articles)}개)</h3>
        {''.join(f'''
        <div class="article">
            <h3><a href="{article.link}" target="_blank" class="flutter-article-link">{article.title}</a></h3>
            <div class="source">Medium Blog - {format_date_tuple(get_article_date(article))}</div>
        </div>
        ''' for article in flutter_articles)}

        <h3>🤖 Android Developer News ({len(android_articles)}개)</h3>
        {''.join(f'''
        <div class="article">
            <h3><a href="{article.link}" target="_blank" class="android-article-link">{article.title}</a></h3>
            <div class="source">Android Developers - {format_date_tuple(get_article_date(article))}</div>
        </div>
        ''' for article in android_articles)}
    </div>
</body>
</html>
"""

    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"✅ HTML 파일 생성 완료: {filename}")
    return filename


def send_notification_and_open(title, message, filepath):
    """herald로 알림을 보내고, 클릭 시 HTML 리포트를 엽니다."""
    abs_filepath = os.path.abspath(filepath)
    herald = shutil.which("herald")

    if not herald:
        print("⚠ herald가 설치되어 있지 않습니다.")
        print("   brew install mdsakalu/tap/herald")
        print(f"   HTML 파일: {abs_filepath}")
        return

    if not os.path.isfile(abs_filepath):
        print(f"⚠ HTML 파일을 찾을 수 없습니다: {abs_filepath}")
        return

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
        print("   알림을 클릭하면 리포트가 열립니다.")
        return

    error = result.stderr.strip() or result.stdout.strip() or "알 수 없는 오류"
    print(f"⚠ 알림 실패: {error}")
    print("   시스템 설정 → 알림 → Herald 에서 '알림 허용'을 확인해 주세요.")
    print(f"   HTML 파일: {abs_filepath}")


if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY 환경 변수를 설정해 주세요.")

    print("🔍 개발자 뉴스 수집 중...")

    apple_articles = fetch_apple_news()
    flutter_articles = fetch_flutter_news()
    android_articles = fetch_android_news()

    print("🤖 Gemini로 Apple News 요약 중...")
    apple_summary = summarize_apple_with_gemini(apple_articles)

    print("🤖 Gemini로 Flutter News 요약 중...")
    flutter_summary = summarize_flutter_with_gemini(flutter_articles)

    print("🤖 Gemini로 Android News 요약 중...")
    android_summary = summarize_android_with_gemini(android_articles)

    print("📝 HTML 파일 생성 중...")
    filename = generate_html(
        apple_summary,
        flutter_summary,
        android_summary,
        apple_articles,
        flutter_articles,
        android_articles,
    )

    print(f"\n완료! 브라우저에서 {filename} 파일을 열어보세요.")

    total_articles = len(apple_articles) + len(flutter_articles) + len(android_articles)
    send_notification_and_open(
        "📰 모바일 개발자 뉴스 요약 완료",
        f"Apple, Flutter, Android 뉴스가 준비되었습니다. ({total_articles}건)",
        filename,
    )
