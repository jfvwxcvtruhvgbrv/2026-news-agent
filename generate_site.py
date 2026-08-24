"""
archive/{날짜}.json 파일들을 읽어서 정적 HTML 아카이브 사이트를 생성한다.
- 각 날짜별 페이지: 그날 생성된 카테고리들과, 카테고리 내부의 다중 관점 카드
- index.html: 날짜별 아카이브 목록
"""
import json
import glob
import os

OUTPUT_DIR = "site"
ARCHIVE_DIR = "archive"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{date} 아카이브</title>
<style>
  body {{ font-family: -apple-system, "Noto Sans KR", sans-serif; max-width: 900px;
         margin: 0 auto; padding: 24px; background: #f7f5f2; color: #1a1a1a; }}
  h1 {{ font-size: 28px; border-bottom: 3px solid #1a1a1a; padding-bottom: 8px; }}
  .category {{ margin: 32px 0; }}
  .category-name {{ font-size: 20px; font-weight: 700; background: #1a1a1a; color: #fff;
                     display: inline-block; padding: 4px 12px; border-radius: 4px; }}
  .category-reason {{ color: #666; font-size: 13px; margin: 6px 0 16px; }}
  .story {{ background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .topic-summary {{ font-weight: 600; margin-bottom: 12px; }}
  .perspectives {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 12px; }}
  .perspective {{ border-left: 4px solid #c0392b; background: #fafafa; padding: 10px 12px; }}
  .viewpoint-label {{ font-weight: 700; font-size: 13px; color: #c0392b; margin-bottom: 4px; }}
  .perspective-summary {{ font-size: 14px; line-height: 1.5; }}
  .source-link {{ display: block; margin-top: 8px; font-size: 12px; }}
  a.back {{ display: inline-block; margin-bottom: 16px; }}
</style>
</head>
<body>
  <a class="back" href="index.html">&larr; 전체 아카이브로</a>
  <h1>{date}</h1>
  {categories_html}
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><title>뉴스 아카이브</title>
<style>
  body {{ font-family: -apple-system, "Noto Sans KR", sans-serif; max-width: 700px;
         margin: 0 auto; padding: 24px; }}
  li {{ margin: 8px 0; font-size: 16px; }}
</style>
</head>
<body>
  <h1>뉴스 아카이브</h1>
  <ul>{items}</ul>
</body>
</html>
"""


def render_story(story: dict) -> str:
    perspectives_html = "".join(
        f"""
        <div class="perspective">
          <div class="viewpoint-label">{p.get('viewpoint_label','')}</div>
          <div class="perspective-summary">{p.get('summary','')}</div>
          <a class="source-link" href="{p.get('link','#')}" target="_blank">
            출처: {p.get('source','')}
          </a>
        </div>"""
        for p in story.get("perspectives", [])
    )
    return f"""
    <div class="story">
      <div class="topic-summary">{story.get('topic_summary','')}</div>
      <div class="perspectives">{perspectives_html}</div>
    </div>"""


def render_category(cat: dict) -> str:
    stories_html = "".join(render_story(s) for s in cat.get("stories", []))
    return f"""
    <div class="category">
      <div class="category-name">{cat.get('category_name','')}</div>
      <div class="category-reason">{cat.get('category_reason','')}</div>
      {stories_html}
    </div>"""


def build_site():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    archive_files = sorted(glob.glob(f"{ARCHIVE_DIR}/*.json"), reverse=True)

    index_items = []
    for path in archive_files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        date = data["date"]
        categories_html = "".join(render_category(c) for c in data.get("categories", []))
        page_html = PAGE_TEMPLATE.format(date=date, categories_html=categories_html)
        with open(f"{OUTPUT_DIR}/{date}.html", "w", encoding="utf-8") as f:
            f.write(page_html)
        index_items.append(f'<li><a href="{date}.html">{date}</a></li>')

    index_html = INDEX_TEMPLATE.format(items="".join(index_items))
    with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"{len(archive_files)}개 날짜 페이지 생성 완료 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    build_site()
