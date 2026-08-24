# 전세계 타블로이드 뉴스 아카이브 — 완전 자동화 버전

그날그날 뉴스/커뮤니티를 모아 **동적으로 카테고리를 만들고**, 사안에
여러 시각이 있으면 **관점별로 나란히** 정리해서 매일 자동으로 쌓이는
개인 아카이브 사이트입니다. 한 번 세팅해두면 이후엔 신경 쓸 필요 없이
매일 자동으로 돌아갑니다.

## 지금 사용자님이 해야 할 일은 딱 3가지뿐입니다

### 1. GitHub 저장소 만들기
- github.com 에서 새 저장소(Repository) 생성 (Public으로)
- 이 폴더 전체(파일들)를 그 저장소에 업로드

### 2. API 키를 비밀값(Secret)으로 등록
- 저장소의 **Settings → Secrets and variables → Actions → New repository secret**
- 이름: `ANTHROPIC_API_KEY`
- 값: [console.anthropic.com](https://console.anthropic.com)에서 발급받은 API 키

### 3. GitHub Pages 켜기
- 저장소의 **Settings → Pages → Build and deployment → Source**를
  "GitHub Actions"로 설정

**이게 끝입니다.** 이후로는 매일 한국시간 아침 6시에 자동으로:
뉴스/커뮤니티 수집 → 카테고리 분류 + 다중 관점 요약 → 사이트 생성 →
`https://[사용자이름].github.io/[저장소이름]/` 에 자동 배포됩니다.

바로 오늘 실행해보고 싶다면, 저장소의 **Actions 탭 → "매일 뉴스 아카이브
생성 및 배포" → Run workflow** 버튼을 눌러 수동으로도 즉시 실행할 수
있습니다.

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

## 로컬에서 미리 테스트하고 싶다면 (선택사항)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python3 run_pipeline.py
open site/index.html   # 결과 미리보기
```

## 법적/윤리적 원칙 (이미 코드에 내장되어 있음)

- 원문 전체를 저장하지 않고, RSS의 짧은 발췌 + Claude가 재구성한
  2~3문장 요약만 사용합니다.
- 모든 카드에 원문 출처와 링크가 항상 표시됩니다.
- 여러 시각이 있는 사안은 하나로 뭉개지 않고 관점별로 병기합니다.
- 커뮤니티 사이트(Reddit 등)를 상업적으로 크게 키울 계획이면 추후
  공식 API(OAuth)로 전환을 검토하세요.

## 나중에 확장하고 싶어지면

- `config.py`에 원하는 국가 타블로이드 추가 (RSS 주소만 넣으면 됨)
- 이메일 뉴스레터 발송 (Resend/Mailchimp 등 연동)
- 커스텀 도메인 연결 (GitHub Pages 설정에서 가능)
- 디자인은 이후 클로드 디자인으로 `site/` HTML을 다듬어도 됨
