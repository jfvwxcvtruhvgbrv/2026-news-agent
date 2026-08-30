"""
archive/{날짜}.json (스키마: global_picture + issues)을 읽어
Global News Intelligence 스타일 정적 HTML 사이트를 생성한다.

- 각 날짜별 페이지: site/{date}.html
- index.html: 날짜별 아카이브 목록 (site/index.html)

build_site()의 시그니처와 OUTPUT_DIR/ARCHIVE_DIR 상수는 기존과 동일하게
유지했다 — run_pipeline.py 등 다른 파일은 수정할 필요가 없다.
"""
import json
import glob
import os

OUTPUT_DIR = "site"
ARCHIVE_DIR = "archive"

# ── 추세 상태 → 한글 라벨 / 색 / 게이지 단계 ─────────────────────────
TREND_LABEL = {
    "Accelerating": "빠르게 확산",
    "Developing":   "지속 전개",
    "Emerging":     "새로운 신호",
    "Structural":   "구조적 흐름",
    "Cooling":      "잦아드는 흐름",
}
TREND_COLOR = {
    "Accelerating": "#B43B2E",
    "Developing":   "#2C5C87",
    "Emerging":     "#A6790F",
    "Structural":   "#5A6270",
    "Cooling":      "#3F7A5D",
}
TREND_STEPS = {
    "Accelerating": 4,
    "Developing":   3,
    "Emerging":     2,
    "Structural":   2,
    "Cooling":      1,
}
DEFAULT_TREND_COLOR = "#5A6270"

# ── 다중 관점(perspectives)의 frame 이름 → 색 (키워드 매칭) ─────────
LENS_KEYWORDS = [
    ("military",   "#454E5B"),
    ("political",  "#7E3040"),
    ("economic",   "#8F6A17"),
    ("technology", "#1D6B60"),
    ("social",     "#564A85"),
]
DEFAULT_LENS_COLOR = "#4B515C"

# ── 오늘의 세계(글로벌 픽처) 보드 컬럼 정의 ──────────────────────────
BOARD_COLUMNS = [
    ("world_right_now",     "지금 세계에서",       "#12151C"),
    ("emerging_signals",    "새롭게 감지된 신호",  "#A6790F"),
    ("structural_trends",   "지속되는 구조적 흐름", "#5A6270"),
    ("what_changed_today",  "어제와 달라진 점",    "#2C5C87"),
    ("what_to_watch_next",  "다음에 확인할 것",    "#B43B2E"),
]

INSIGHT_LABELS = [
    ("what_happened",   "무슨 일이"),
    ("why_it_matters",  "왜 중요한가"),
    ("what_is_changing","무엇이 달라지는가"),
    ("connection",      "연결점"),
    ("signal",          "시그널"),
    ("what_to_watch",   "지켜볼 것"),
]

WD = ["월", "화", "수", "목", "금", "토", "일"]


def _pretty_date(date_str: str) -> str:
    import datetime as dt
    try:
        d = dt.date.fromisoformat(date_str)
        return f"{d.year}년 {d.month}월 {d.day}일 {WD[d.weekday()]}요일"
    except Exception:
        return date_str


def _lens_color(frame: str) -> str:
    f = (frame or "").lower()
    for kw, color in LENS_KEYWORDS:
        if kw in f:
            return color
    return DEFAULT_LENS_COLOR


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── 렌더 함수들 ──────────────────────────────────────────────────────

def render_global_picture(global_picture: dict) -> str:
    if not global_picture:
        return ""
    cols = []
    for key, label, color in BOARD_COLUMNS:
        items = global_picture.get(key) or []
        if not items:
            continue
        lis = "".join(
            f'<li><i style="background:{color}"></i><span>{_esc(t)}</span></li>'
            for t in items
        )
        cols.append(
            f'<div class="board-col"><h3><span class="dot" style="background:{color}"></span>{label}</h3>'
            f'<ul>{lis}</ul></div>'
        )
    if not cols:
        return ""
    return f'<div class="board"><div class="board-grid">{"".join(cols)}</div></div>'


def render_insight(insight: dict) -> str:
    if not insight:
        return ""
    items = []
    for key, label in INSIGHT_LABELS:
        val = insight.get(key)
        if not val:
            continue
        items.append(
            f'<div class="field"><b>{label}</b><p>{_esc(val)}</p></div>'
        )
    if not items:
        return ""
    return f'<div class="fields">{"".join(items)}</div>'


def render_perspectives(perspectives: list) -> str:
    if not perspectives:
        return ""
    boxes = []
    for p in perspectives:
        frame = p.get("frame", "")
        color = _lens_color(frame)
        boxes.append(
            f'<div class="lens" style="border-top-color:{color}">'
            f'<div class="lh"><i style="background:{color}"></i>{_esc(frame)}</div>'
            f'<p>{_esc(p.get("summary",""))}</p></div>'
        )
    return f'<div class="lenses">{"".join(boxes)}</div>'


def render_sources(sources: list) -> str:
    if not sources:
        return ""
    links = "".join(
        f'<a class="src" href="{_esc(s.get("link","#"))}" target="_blank" rel="noopener">'
        f'{_esc(s.get("source",""))}<small>({_esc(s.get("region",""))})</small></a>'
        for s in sources
    )
    return f'<div class="sources"><span class="lbl">출처</span>{links}</div>'


def render_issue(issue: dict, case_id: str) -> str:
    trend = issue.get("trend_status", "")
    label = TREND_LABEL.get(trend, trend or "이슈")
    color = TREND_COLOR.get(trend, DEFAULT_TREND_COLOR)
    steps = TREND_STEPS.get(trend, 2)
    gauge = "".join(
        f'<i style="background:{color}"></i>' if i < steps else '<i></i>'
        for i in range(4)
    )
    return f"""
    <div class="case">
      <div class="case-head">
        <div>
          <div class="case-id">{case_id}</div>
          <div class="case-title">{_esc(issue.get('headline',''))}</div>
        </div>
        <div class="velocity">
          <div class="label" style="color:{color}">{label}</div>
          <div class="gauge">{gauge}</div>
        </div>
      </div>
      {render_insight(issue.get('insight', {}))}
      {render_perspectives(issue.get('perspectives', []))}
      {render_sources(issue.get('sources', []))}
    </div>"""


# ── 페이지 템플릿 (서체: Pretendard 하나로 통일, 좌우 여백 5vw) ──────

BASE_CSS = """
:root{
  --paper:#E7EBEE; --card:#F6F8F9;
  --ink:#12151C; --ink-soft:#4B515C; --rule:#C6CCD3;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);color:var(--ink);
  font-family:"Pretendard",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;
  font-size:16px;line-height:1.65;word-break:keep-all;-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{padding:0 5vw}
.back{display:inline-block;margin:26px 0 6px;font-size:13px;color:var(--ink-soft);
  text-decoration:none;border-bottom:1px solid var(--rule)}
.back:hover{border-color:var(--ink);color:var(--ink)}
.headline{font-weight:800;font-size:clamp(26px,4vw,42px);letter-spacing:-.01em;margin:10px 0 6px}
.metarow{display:flex;gap:20px;flex-wrap:wrap;margin:14px 0 30px;font-size:13px;color:var(--ink-soft)}
.metarow .m{display:flex;align-items:center;gap:7px}
.dot{width:8px;height:8px;border-radius:50%;flex:none}

.board{margin:0 0 40px}
.board-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--rule);border:1px solid var(--rule)}
.board-col{background:var(--card);padding:16px 16px 18px}
.board-col h3{font-size:12px;letter-spacing:.06em;color:var(--ink-soft);margin-bottom:10px;
  display:flex;align-items:center;gap:7px;font-weight:700}
.board-col ul{list-style:none}
.board-col li{display:flex;gap:8px;padding:7px 0;border-top:1px solid var(--rule);font-size:13px;line-height:1.5}
.board-col li:first-child{border-top:none}
.board-col li i{width:5px;height:5px;border-radius:50%;flex:none;margin-top:6px}
@media (max-width:1100px){.board-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width:600px){.board-grid{grid-template-columns:1fr}}

.section-title{font-weight:800;font-size:19px;margin:36px 0 14px}

.case{background:var(--card);border:1px solid var(--rule);margin-bottom:24px}
.case-head{padding:18px 20px;border-bottom:1px solid var(--rule);
  display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap}
.case-id{font-size:11px;color:var(--ink-soft);letter-spacing:.05em;margin-bottom:8px}
.case-title{font-weight:800;font-size:19px;line-height:1.4;max-width:760px}
.velocity{flex:none;display:flex;flex-direction:column;align-items:flex-end;gap:6px}
.velocity .label{font-size:12px;font-weight:700;letter-spacing:.03em}
.gauge{display:flex;gap:3px}
.gauge i{width:16px;height:5px;border-radius:1px;background:var(--rule)}

.fields{display:grid;grid-template-columns:repeat(2,1fr)}
.field{padding:15px 20px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.field:nth-child(2n){border-right:none}
.field b{display:block;font-size:11px;letter-spacing:.04em;color:#B43B2E;margin-bottom:6px;font-weight:700}
.field p{font-size:14px;color:var(--ink-soft);line-height:1.55}
@media (max-width:640px){.fields{grid-template-columns:1fr}.field{border-right:none}}

.lenses{display:flex;flex-wrap:wrap;border-bottom:1px solid var(--rule)}
.lens{flex:1 1 220px;padding:13px 20px;border-right:1px solid var(--rule);border-top:4px solid transparent}
.lens:last-child{border-right:none}
.lens .lh{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;margin-bottom:6px}
.lens .lh i{width:8px;height:8px;border-radius:50%}
.lens p{font-size:13.5px;color:var(--ink-soft);line-height:1.55}
@media (max-width:820px){.lenses{flex-direction:column}.lens{border-right:none;border-bottom:1px solid var(--rule)}}

.sources{padding:12px 20px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.sources .lbl{font-size:11px;letter-spacing:.04em;color:var(--ink-soft)}
.src{font-size:13px;text-decoration:none;border-bottom:1px solid var(--rule)}
.src:hover{border-color:var(--ink)}
.src small{color:var(--ink-soft);margin-left:3px}
.foot{padding:24px 0 60px;font-size:11px;color:var(--ink-soft)}

.log-row{display:grid;grid-template-columns:150px 1fr auto;gap:20px;align-items:center;
  padding:22px 0;border-top:1px solid var(--rule);text-decoration:none}
.log-row:last-child{border-bottom:1px solid var(--rule)}
.rdate{font-weight:700;font-size:16px;white-space:nowrap}
.rteaser{font-size:15px;color:var(--ink-soft);display:-webkit-box;-webkit-line-clamp:1;
  -webkit-box-orient:vertical;overflow:hidden}
.rarrow{font-size:13px;color:var(--ink-soft)}
.log-row:hover .rteaser{color:var(--ink)}
@media (max-width:600px){.log-row{grid-template-columns:1fr}.rarrow{display:none}}
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{date} — Global News Intelligence</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="index.html">&larr; 전체 아카이브로</a>
  <div class="headline">{pretty_date}</div>
  <div class="metarow">{metarow}</div>
  {global_picture_html}
  <div class="section-title">오늘의 이슈</div>
  {issues_html}
  <div class="foot">Global News Intelligence · 자동 수집·분석 브리핑 · 판단 전 원문 확인 요망</div>
</div>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Global News Intelligence — 아카이브</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <div class="headline" style="margin-top:60px">GLOBAL NEWS INTELLIGENCE</div>
  <div style="margin:34px 0 90px">{rows}</div>
</div>
</body>
</html>
"""


def build_site():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    archive_files = sorted(glob.glob(f"{ARCHIVE_DIR}/*.json"), reverse=True)

    log_rows = []
    for path in archive_files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        date = data["date"]
        issues = data.get("issues", [])

        rapid_n = sum(1 for i in issues if i.get("trend_status") == "Accelerating")
        metarow = (
            f'<div class="m"><span class="dot" style="background:{TREND_COLOR["Accelerating"]}"></span>'
            f'빠르게 확산 {rapid_n}건</div>'
            f'<div class="m">이슈 {len(issues)}건 수록</div>'
            f'<div class="m">{_pretty_date(date)}</div>'
        )

        global_picture_html = render_global_picture(data.get("global_picture", {}))
        issues_html = "".join(
            render_issue(issue, f"GNI·{date.replace('-','')}·{idx+1:02d}")
            for idx, issue in enumerate(issues)
        )

        page_html = PAGE_TEMPLATE.format(
            date=date,
            pretty_date=f"{date} — 오늘의 세계",
            metarow=metarow,
            css=BASE_CSS,
            global_picture_html=global_picture_html,
            issues_html=issues_html,
        )
        with open(f"{OUTPUT_DIR}/{date}.html", "w", encoding="utf-8") as f:
            f.write(page_html)

        teaser = issues[0].get("headline", "") if issues else ""
        log_rows.append(
            f'<a class="log-row" href="{date}.html">'
            f'<div class="rdate">{_pretty_date(date)}</div>'
            f'<div class="rteaser">{_esc(teaser)}</div>'
            f'<div class="rarrow">열기 →</div></a>'
        )

    index_html = INDEX_TEMPLATE.format(css=BASE_CSS, rows="".join(log_rows))
    with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"{len(archive_files)}개 날짜 페이지 생성 완료 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    build_site()
