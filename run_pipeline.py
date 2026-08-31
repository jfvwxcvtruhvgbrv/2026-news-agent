"""
전체 파이프라인 원샷 실행 스크립트.

    python3 run_pipeline.py

한 번 실행으로:
1) 오늘 자 뉴스/커뮤니티 수집
2) Claude로 2단계(Map-Reduce) 이슈 클러스터링 + 글로벌 픽처 생성
3) archive/에 JSON 저장 (한국시간 날짜 + 오전/오후 세션 구분)
4) site/에 최신 정적 HTML 생성

까지 전부 처리한다. GitHub Actions가 이 스크립트를 하루 두 번(아침/저녁)
자동으로 실행한다.
"""
import json
import os
import sys
import datetime as dt

from fetch_sources import fetch_today
from cluster_and_summarize import build_daily_archive
from generate_site import build_site


def main():
    print("[1/3] 오늘 자 뉴스/커뮤니티 수집 중...")
    items = fetch_today()
    print(f"    → {len(items)}개 아이템 수집")

    if not items:
        print("    수집된 아이템이 없어 종료합니다 (소스 접근 실패 여부 확인 필요).")
        sys.exit(0)

    print("[2/3] Claude로 2단계(Map-Reduce) 이슈 클러스터링 + 글로벌 픽처 생성 중...")
    archive = build_daily_archive(items)
    os.makedirs("archive", exist_ok=True)

    # 파일명에 한국시간 날짜 + 세션(오전/오후)을 반영해 하루 두 번 실행해도
    # 서로 덮어쓰지 않고 별도 아카이브로 남긴다.
    date = archive["date"]
    session = archive.get("session")
    slug = f"{date}-{session}" if session else date

    out_path = f"archive/{slug}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)
    print(f"    → {out_path} 저장 완료 (이슈 {len(archive.get('issues', []))}건)")

    print("[3/3] 정적 사이트(site/) 생성 중...")
    build_site()
    print("완료.")


if __name__ == "__main__":
    main()
