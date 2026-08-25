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
# 허용하는 채널이다. (전체 목록은 각 사이트에서 실제 RSS 주소를 재확인할 것.
# RSS 주소는 언론사 사정으로 종종 바뀌므로 수집 실패 로그가 늘어나면
# 해당 소스의 최신 RSS 주소를 다시 확인해야 한다.)
#
# 각 소스는 (RSS 주소, 지역 태그) 튜플로 관리한다. 지역 태그는 글로벌
# 커버리지 균형을 점검하고, Claude에게 "이 기사가 어느 지역 소스인지"
# 명시적으로 알려주기 위한 메타데이터로만 쓰인다 (강제 균등 배분 아님).
NEWS_FEEDS = {
    # North America
    "NY Post": ("https://nypost.com/feed/", "North America"),
    "Reuters World": ("https://www.reutersagency.com/feed/?best-topics=world&post_type=best", "North America"),
    # Europe (UK 포함)
    "Daily Mail (UK)": ("https://www.dailymail.co.uk/articles.rss", "Europe"),
    "The Sun (UK)": ("https://www.thesun.co.uk/feed/", "Europe"),
    "Mirror (UK)": ("https://www.mirror.co.uk/news/rss.xml", "Europe"),
    "BBC World": ("http://feeds.bbci.co.uk/news/world/rss.xml", "Europe"),
    "DW English": ("https://rss.dw.com/rdf/rss-en-all", "Europe"),
    "France24 English": ("https://www.france24.com/en/rss", "Europe"),
    # China / East Asia
    "SCMP (Hong Kong)": ("https://www.scmp.com/rss/91/feed", "China"),
    "NHK World Japan": ("https://www3.nhk.or.jp/nhkworld/en/news/all.xml", "Japan"),
    "Korea Herald": ("http://www.koreaherald.com/rss/020000000000.xml", "Korea"),
    # South Asia / Southeast Asia
    "Times of India": ("https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "India"),
    "Straits Times (Singapore)": ("https://www.straitstimes.com/news/asia/rss.xml", "Southeast Asia"),
    # Middle East
    "Al Jazeera": ("https://www.aljazeera.com/xml/rss/all.xml", "Middle East"),
    # Africa
    "AllAfrica": ("https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf", "Africa"),
    # Latin America
    "MercoPress": ("https://en.mercopress.com/rss/", "Latin America"),
    # Oceania
    "News.com.au": ("https://www.news.com.au/content-feeds/latest-news-national/", "Oceania"),
    "NZ Herald": ("https://www.nzherald.co.nz/arc/outboundfeeds/rss/", "Oceania"),
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
