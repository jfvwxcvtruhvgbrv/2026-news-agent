# 전세계 타블로이드 뉴스 아카이브

그날그날 뉴스/커뮤니티를 모아 **동적으로 카테고리를 만들고**, 사안에
여러 시각이 있으면 **관점별로 나란히** 정리해서 매일 자동으로 쌓이는
개인 아카이브 사이트입니다. 


## 파일 구조

```
run_pipeline.py             전체 과정을 한 번에 실행하는 진입점
config.py                   뉴스 RSS / 커뮤니티 소스 목록
fetch_sources.py            오늘 자 아이템 수집
cluster_and_summarize.py    Claude API로 동적 카테고리화 + 다중 관점 요약
generate_site.py            아카이브 JSON → 정적 HTML 사이트
.github/workflows/daily.yml 매일 자동 실행 + Pages 배포 설정
archive/                    날짜별 원본 데이터 (자동 누적)
site/                       배포되는 최종 HTML (자동 생성)
```
