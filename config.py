"""
소스 설정 파일

법적 안전 원칙:
- RSS/공개 API로 제공되는 '제목 + 짧은 발췌(summary)'만 수집한다.
- 원문 본문 전체를 저장/재게시하지 않는다.
- 각 소스의 robots.txt / 이용약관을 준수한다 (특히 커뮤니티 사이트는
  요청 빈도를 낮게 유지하고, User-Agent를 명시한다).
- 최종 사이트에는 항상 원문 링크를 함께 노출한다 (출처 표시).

소스 확장 메모 (2026-09):
- 기존 지역별 종합 뉴스에 더해, 경영자·투자자 관점에 필요한
  '경제/시장', '기술/AI', '에너지', '과학' 주제별 소스를 신규 추가했다.
- region 필드는 지리적 지역뿐 아니라 주제 태그로도 쓴다 (예: "Business",
  "Technology"). Claude가 이슈를 분류할 때 참고하는 메타데이터일 뿐,
  강제 균등 배분은 아니다.
- RSS 주소는 언론사 사정으로 종종 바뀐다. 수집 실패 로그
  (`[WARN] ... RSS 수집 실패`)가 반복되는 소스는 최신 주소로
  교체하거나 제거할 것.
"""

# ── 뉴스 소스 (RSS 피드) ──────────────────────────────
NEWS_FEEDS = {
    # ── North America ──
    "NY Post": ("https://nypost.com/feed/", "North America"),
    "Reuters World": ("https://www.reutersagency.com/feed/?best-topics=world&post_type=best", "North America"),
    "NPR News": ("https://feeds.npr.org/1004/rss.xml", "North America"),
    "CBC News Top Stories": ("https://www.cbc.ca/cmlink/rss-topstories", "North America"),

    # ── Europe (UK 포함) ──
    "Daily Mail (UK)": ("https://www.dailymail.co.uk/articles.rss", "Europe"),
    "The Sun (UK)": ("https://www.thesun.co.uk/feed/", "Europe"),
    "Mirror (UK)": ("https://www.mirror.co.uk/news/rss.xml", "Europe"),
    "BBC World": ("http://feeds.bbci.co.uk/news/world/rss.xml", "Europe"),
    "The Guardian World": ("https://www.theguardian.com/world/rss", "Europe"),
    "DW English": ("https://rss.dw.com/rdf/rss-en-all", "Europe"),
    "France24 English": ("https://www.france24.com/en/rss", "Europe"),

    # ── China / East Asia ──
    "SCMP (Hong Kong)": ("https://www.scmp.com/rss/91/feed", "China"),
    "Xinhua English": ("http://www.xinhuanet.com/english/rss/worldrss.xml", "China"),
    "NHK World Japan": ("https://www3.nhk.or.jp/nhkworld/en/news/all.xml", "Japan"),
    "Japan Times": ("https://www.japantimes.co.jp/feed/", "Japan"),
    "Korea Herald": ("http://www.koreaherald.com/rss/020000000000.xml", "Korea"),
    "Yonhap English": ("https://en.yna.co.kr/RSS/news.xml", "Korea"),

    # ── South Asia / Southeast Asia ──
    "Times of India": ("https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "India"),
    "The Hindu (International)": ("https://www.thehindu.com/news/international/feeder/default.rss", "India"),
    "Straits Times (Singapore)": ("https://www.straitstimes.com/news/asia/rss.xml", "Southeast Asia"),
    "Bangkok Post": ("https://www.bangkokpost.com/rss/data/topstories.xml", "Southeast Asia"),

    # ── Middle East ──
    "Al Jazeera": ("https://www.aljazeera.com/xml/rss/all.xml", "Middle East"),
    "Times of Israel": ("https://www.timesofisrael.com/feed/", "Middle East"),
    "The National (UAE)": ("https://www.thenationalnews.com/arc/outboundfeeds/rss/", "Middle East"),

    # ── Africa ──
    "AllAfrica": ("https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf", "Africa"),
    "BBC Africa": ("http://feeds.bbci.co.uk/news/world/africa/rss.xml", "Africa"),

    # ── Latin America ──
    "MercoPress": ("https://en.mercopress.com/rss/", "Latin America"),
    "Rio Times": ("https://www.riotimesonline.com/feed/", "Latin America"),

    # ── Oceania ──
    "News.com.au": ("https://www.news.com.au/content-feeds/latest-news-national/", "Oceania"),
    "NZ Herald": ("https://www.nzherald.co.nz/arc/outboundfeeds/rss/", "Oceania"),
    "ABC News Australia": ("https://www.abc.net.au/news/feed/45910/rss.xml", "Oceania"),

    # ── Business / Markets (서구+아시아 균형) ──
    "Reuters Business": ("https://www.reutersagency.com/feed/?best-topics=business&post_type=best", "Business"),
    "CNBC Top News": ("https://www.cnbc.com/id/100003114/device/rss/rss.html", "Business"),
    "CoinDesk": ("https://www.coindesk.com/arc/outboundfeeds/rss/", "Business"),
    "Economic Times (India)": ("https://economictimes.indiatimes.com/rssfeedstopstories.cms", "Business"),

    # ── Technology / AI (신규) ──
    "TechCrunch": ("https://techcrunch.com/feed/", "Technology"),
    "Ars Technica": ("https://feeds.arstechnica.com/arstechnica/index", "Technology"),

    # ── Energy / Commodities (신규) ──
    "OilPrice.com": ("https://oilprice.com/rss/main", "Energy"),

    # ── Science / Health (신규) ──
    "ScienceDaily": ("https://www.sciencedaily.com/rss/all.xml", "Science"),
    "Nature News": ("http://feeds.nature.com/nature/rss/current", "Science"),

    # ── Culture / Entertainment (신규) ──
    "Variety": ("https://variety.com/feed/", "Culture"),
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
    "Reddit r/geopolitics": "https://www.reddit.com/r/geopolitics/top.json?limit=25&t=day",
    "Reddit r/economics": "https://www.reddit.com/r/economics/top.json?limit=25&t=day",
    "Reddit r/technology": "https://www.reddit.com/r/technology/top.json?limit=25&t=day",
    "Hacker News Top": "https://hacker-news.firebaseio.com/v0/topstories.json",
}

REQUEST_USER_AGENT = "personal-archive-bot/0.1 (contact: your-email@example.com)"
REQUEST_DELAY_SECONDS = 2  # 사이트별 과도한 요청 방지

# Claude API 모델 (클러스터링/다중관점 요약에 사용)
CLAUDE_MODEL = "claude-sonnet-4-6"
