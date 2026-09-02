name: 매일 뉴스 아카이브 생성 및 배포

on:
  schedule:
    # 한국시간 04:00~05:59 사이 15분마다 시도 (목표 04:00, 새벽 수집)
    - cron: "*/15 19,20 * * *"
    # 한국시간 16:00~17:59 사이 15분마다 시도 (목표 16:00, 새벽 수집으로부터 12시간 뒤)
    - cron: "*/15 7,8 * * *"
  workflow_dispatch:        # 수동 실행 버튼도 사용 가능

permissions:
  contents: write
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: 저장소 체크아웃
        uses: actions/checkout@v4

      - name: 파이썬 설치
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: 의존성 설치
        run: pip install -r requirements.txt

      - name: 파이프라인 실행 (수집 → 분류/요약 → 사이트 생성)
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python3 run_pipeline.py

      - name: 생성된 아카이브(JSON) 커밋
        run: |
          git config user.name "news-archive-bot"
          git config user.email "bot@users.noreply.github.com"
          git add archive/
          git diff --quiet && git diff --staged --quiet || git commit -m "일일 아카이브 자동 업데이트 $(date -u +%F)"
          git push

      - name: GitHub Pages 아티팩트 업로드
        uses: actions/upload-pages-artifact@v3
        with:
          path: site

      - name: GitHub Pages 배포
        uses: actions/deploy-pages@v4
