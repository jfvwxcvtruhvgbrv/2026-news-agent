"""
소스 설정 파일

법적 안전 원칙:
- RSS/공개 API로 제공되는 '제목 + 짧은 발췌(summary)'만 수집한다.
- 원문 본문 전체를 저장/재게시하지 않는다.
- 각 소스의 robots.txt / 이용약관을 준수한다 (특히 커뮤니티 사이트는
  요청 빈도를 낮게 유지하고, User-Agent를 명시한다).
- 최종 사이트에는 항상 원문 링크를 함께 노출한다 (출처 표시).
"""

# ── 뉴스 소스 (RSS 피드) ──────────────────────────────
# 대부분의 언론사는 공식 RSS를 제공하며, 이는 명시적으로 구독/집계를
# 허용하는 채널이다. (전체 목록은 각 사이트에서 실제 RSS 주소를 재확인할 것)
NEWS_FEEDS = {
    "NY Post": "https://nypost.com/feed/",
    "Daily Mail (UK)": "https://www.dailymail.co.uk/articles.rss",
    "The Sun (UK)": "https://www.thesun.co.uk/feed/",
    "Mirror (UK)": "https://www.mirror.co.uk/news/rss.xml",
    "News.com.au": "https://www.news.com.au/content-feeds/latest-news-national/",
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters World": "https://feeds.reuters.com/Reuters/worldNews",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
}

# ── 커뮤니티 소스 (공개 JSON 엔드포인트) ─────────────────
# Reddit의 .json 엔드포인트는 로그인 없이 공개적으로 접근 가능하지만
# 이용약관상 과도한 자동 수집은 제한될 수 있으므로 요청 간격을 두고,
# 명확한 User-Agent를 지정해야 한다. 상업적 대량 이용 시 공식 API
# (OAuth) 사용을 권장한다.
COMMUNITY_SOURCES = {
    "Reddit r/worldnews": "https://www.reddit.com/r/worldnews/top.json?limit=25&t=day",
    "Reddit r/nottheonion": "https://www.reddit.com/r/nottheonion/top.json?limit=25&t=day",
    "Reddit r/news": "https://www.reddit.com/r/news/top.json?limit=25&t=day",
    "Hacker News Top": "https://hacker-news.firebaseio.com/v0/topstories.json",
}

REQUEST_USER_AGENT = "personal-archive-bot/0.1 (contact: your-email@example.com)"
REQUEST_DELAY_SECONDS = 2  # 사이트별 과도한 요청 방지

# Claude API 모델 (클러스터링/다중관점 요약에 사용)
CLAUDE_MODEL = "claude-sonnet-4-6"
