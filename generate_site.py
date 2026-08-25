"""
archive/{날짜}.json (새 스키마: global_picture + issues)을 읽어서
Global News Intelligence 스타일의 정적 HTML 사이트를 생성한다.
"""
import json
import glob
import os

OUTPUT_DIR = "site"
ARCHIVE_DIR = "archive"

TREND_LABEL = {
    "Emerging": "🌱 새로 등장",
    "Accelerating": "🚀 빠르게 확산",
    "Developing": "📈 지속 전개",
    "Structural": "🏛 구조적 변화",
    "Cooling": "🧊 관심 감소",
}

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{date} — 오늘의 세계</title>
<style>
  body {{ font-family: -apple-system, "Noto Sans KR", sans-serif; max-width: 920px;
         margin: 0 auto; padding: 24px; background: #f7f5f2; color: #1a1a1a;
         line-height: 1.55; }}
  h1 {{ font-size: 26px; border-bottom: 3px solid #1a1a1a; padding-bottom: 8px; }}
  h2.section-title {{ font-size: 15px; text-transform: uppercase; letter-spacing: 0.05em;
                       color: #888; margin: 32px 0 8px; }}
  .picture-box {{ background: #fff; border-radius: 8px; padding: 16px 20px; margin-bottom: 8px;
                  box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  .picture-box ul {{ margin: 4px 0 0; padding-left: 18px; }}
  .picture-box li {{ margin: 4px 0; }}
  .issue {{ background: #fff; border-radius: 10px; padding: 20px; margin: 20px 0;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
  .headline {{ font-size: 19px; font-weight: 700; margin-bottom: 6px; }}
  .trend-badge {{ display: inline-block; font-size: 12px; background: #1a1a1a; color: #fff;
                  padding: 2px 10px; border-radius: 999px; margin-bottom: 12px; }}
  .insight-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                    gap: 10px; margin: 12px 0; }}
  .insight-item {{ background: #fafafa; border-left: 3px solid #c0392b; padding: 8px 12px; }}
  .insight-label {{ font-size: 11px; font-weight: 700; color: #c0392b; text-transform: uppercase; }}
  .insight-text {{ font-size: 14px; margin-top: 2px; }}
  .perspectives {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }}
  .perspective {{ background: #eef2f7; border-radius: 6px; padding: 8px 12px; font-size: 13px;
                  max-width: 320px; }}
  .frame-label {{ font-weight: 700; font-size: 12px; color: #34495e; }}
  .sources {{ font-size: 12px; color: #666; margin-top: 10px; }}
  .sources a {{ margin-right: 10px; }}
  a.back {{ display: inline-block; margin-bottom: 16px; }}
</style>
</head>
<body>
  <a class="back" href="index.html">&larr; 전체 아카이브로</a>
  <h1>{date} — 오늘의 세계</h1>
  {global_picture_html}
  <h2 class="section-title">오늘의 이슈</h2>
  {issues_html}
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><title>Global News Intelligence 아카이브</title>
<style>
  body {{ font-family: -apple-system, "Noto Sans KR", sans-serif; max-width: 700px;
         margin: 0 auto; padding: 24px; }}
  li {{ margin: 8px 0; font-size: 16px; }}
</style>
</head>
<body>
  <h1>Global News Intelligence 아카이브</h1>
  <ul>{items}</ul>
</body>
</html>
"""

PICTURE_SECTIONS = [
    ("world_right_now", "지금 세계에서"),
    ("emerging_signals", "새롭게 감지된 신호"),
    ("structural_trends", "지속되는 구조적 흐름"),
    ("what_changed_today", "어제와 달라진 점"),
    ("what_to_watch_next", "앞으로 지켜볼 것"),
]


def render_global_picture(gp: dict) -> str:
    boxes = []
    for key, title in PICTURE_SECTIONS:
        entries = gp.get(key) or []
        if not entries:
            continue
        li = "".join(f"<li>{e}</li>" for e in entries)
        boxes.append(
            f'<h2 class="section-title">{title}</h2><div class="picture-box"><ul>{li}</ul></div>'
        )
    return "".join(boxes)


def render_insight(insight: dict) -> str:
    labels = {
        "what_happened": "무슨 일이",
        "why_it_matters": "왜 중요한가",
        "what_is_changing": "무엇이 달라지는가",
        "connection": "연결점",
        "signal": "시그널",
        "what_to_watch": "지켜볼 것",
    }
    items = []
    for key, label in labels.items():
        val = insight.get(key)
        if not val:
            continue
        items.append(
            f'<div class="insight-item"><div class="insight-label">{label}</div>'
            f'<div class="insight-text">{val}</div></div>'
        )
    return f'<div class="insight-grid">{"".join(items)}</div>'


def render_perspectives(perspectives: list) -> str:
    if not perspectives:
        return ""
    cards = "".join(
        f'<div class="perspective"><div class="frame-label">{p.get("frame","")}</div>'
        f'{p.get("summary","")}</div>'
        for p in perspectives
    )
    return f'<div class="perspectives">{cards}</div>'


def render_sources(sources: list) -> str:
    if not sources:
        return ""
    links = "".join(
        f'<a href="{s.get("link","#")}" target="_blank">{s.get("source","")}'
        f' ({s.get("region","")})</a>'
        for s in sources
    )
    return f'<div class="sources">출처: {links}</div>'


def render_issue(issue: dict) -> str:
    trend = issue.get("trend_status", "")
    trend_label = TREND_LABEL.get(trend, trend)
    return f"""
    <div class="issue">
      <div class="headline">{issue.get('headline','')}</div>
      <div class="trend-badge">{trend_label}</div>
      {render_insight(issue.get('insight', {}))}
      {render_perspectives(issue.get('perspectives', []))}
      {render_sources(issue.get('sources', []))}
    </div>"""


def build_site():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    archive_files = sorted(glob.glob(f"{ARCHIVE_DIR}/*.json"), reverse=True)

    index_items = []
    for path in archive_files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        date = data["date"]
        global_picture_html = render_global_picture(data.get("global_picture", {}))
        issues_html = "".join(render_issue(i) for i in data.get("issues", []))
        page_html = PAGE_TEMPLATE.format(
            date=date, global_picture_html=global_picture_html, issues_html=issues_html
        )
        with open(f"{OUTPUT_DIR}/{date}.html", "w", encoding="utf-8") as f:
            f.write(page_html)
        index_items.append(f'<li><a href="{date}.html">{date}</a></li>')

    index_html = INDEX_TEMPLATE.format(items="".join(index_items))
    with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"{len(archive_files)}개 날짜 페이지 생성 완료 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    build_site()
