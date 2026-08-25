"""
수집된 아이템을 Claude API로 넘겨서:
1) 그날그날 실제로 뭉치는 주제에 따라 카테고리를 '동적으로' 생성하고
2) 한 사안 안에 여러 출처의 시각차가 있으면 관점별로 나란히 정리한다.

저작권 원칙(반드시 유지):
- 원문을 그대로 인용하지 않는다. 모든 요약은 재구성된 표현이어야 한다.
- 각 관점 요약은 2~3문장 이내로 짧게.
- 항상 출처명 + 원문 링크를 함께 제공한다.
"""
import json
import os
import datetime as dt

import requests

from config import CLAUDE_MODEL

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

SYSTEM_PROMPT = """\
당신은 전세계 뉴스와 커뮤니티 게시물을 매일 정리하는 아카이빙 에디터입니다.

규칙:
1. 카테고리는 미리 정해진 목록이 아니라, 오늘 주어진 아이템들이 실제로
   묶이는 방식에 따라 당신이 직접 이름을 붙여 생성합니다. 카테고리 개수와
   이름은 그날 데이터에 따라 완전히 달라질 수 있습니다.
2. 같은 사안(스토리)을 다루는 아이템이 여러 출처에서 서로 다른 해석/논조로
   보도되었다면, 이를 하나로 뭉개지 말고 "관점 A / 관점 B / 관점 C" 형태로
   나란히 제시하세요. 관점이 하나뿐이면 하나만 적어도 됩니다.
3. 절대 원문을 그대로 옮기지 마세요(직접 인용 금지). 모든 요약은 당신의
   표현으로 짧게(2~3문장) 재구성해야 합니다.
4. 반드시 아래 JSON 스키마로만 응답하세요. 다른 텍스트, 설명, 코드펜스는
   포함하지 마세요.

출력 스키마:
{
  "categories": [
    {
      "category_name": "string (그날 생성된 카테고리명)",
      "category_reason": "string (왜 오늘 이 카테고리가 형성됐는지 한 줄)",
      "stories": [
        {
          "topic_summary": "string (이 사안이 무엇인지 1~2문장)",
          "perspectives": [
            {
              "viewpoint_label": "string (예: '피해자 측 시각' 등 관점 이름)",
              "summary": "string (2~3문장, 재구성된 표현)",
              "source": "string (원 출처명)",
              "link": "string (원문 링크)"
            }
          ]
        }
      ]
    }
  ]
}
"""


def _call_claude(items: list[dict]) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("환경변수 ANTHROPIC_API_KEY 가 설정되어 있지 않습니다.")

    user_content = (
        "다음은 오늘 수집된 뉴스/커뮤니티 아이템 목록입니다 (JSON). "
        "이 목록을 바탕으로 규칙에 따라 카테고리를 만들고 다중 관점 요약을 생성하세요.\n\n"
        + json.dumps(items, ensure_ascii=False)
    )

    resp = requests.post(
        ANTHROPIC_API_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": CLAUDE_MODEL,
            "max_tokens": 8000,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_content}],
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    text = "".join(
        block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
    )
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


def build_daily_archive(items: list[dict]) -> dict:
    """items(오늘 수집된 원본 리스트)를 받아 카테고리/다중관점 구조로 변환."""
    # 아이템이 너무 많으면 토큰 제한을 넘을 수 있으므로 배치 처리
    # (배치가 너무 크면 Claude 응답이 max_tokens에 걸려 잘리면서 JSON 파싱
    #  에러가 날 수 있어 배치 크기를 작게 유지한다)
    BATCH_SIZE = 25
    all_categories = []
    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i : i + BATCH_SIZE]
        try:
            result = _call_claude(batch)
            all_categories.extend(result.get("categories", []))
        except (json.JSONDecodeError, requests.RequestException) as e:
            # 한 배치가 실패해도 전체 파이프라인은 계속 진행한다
            print(f"[WARN] 배치 {i}~{i+len(batch)} 처리 실패, 건너뜀: {e}")
            continue

    return {
        "date": dt.datetime.utcnow().strftime("%Y-%m-%d"),
        "categories": all_categories,
    }


if __name__ == "__main__":
    with open("raw_input.json", encoding="utf-8") as f:
        items = json.load(f)
    archive = build_daily_archive(items)
    out_path = f"archive/{archive['date']}.json"
    os.makedirs("archive", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)
    print(f"저장 완료 → {out_path}")
