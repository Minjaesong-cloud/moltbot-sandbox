# 신뢰 소스 등록부 — 국제정세·금융·경제·경영·AI

검증된 실존 소스만. **인기≠신뢰.** 유튜브 채널 channel_id는 API로 실제 해결·대조 확인
(추측 없음). 라이브 조회 시 이 목록의 소스만 사용한다.

분류: **durable**(분석틀·방법론·표준 데이터 — 저장·주간 갱신) / **live**(속보·시황·최신 발표 —
조회 시점에 실시간 fetch, 저장 금지).

## 1. 국제정세·지정학

| 소스 | 유형 | 접근 | URL / 채널 | 분류 |
|---|---|---|---|---|
| Council on Foreign Relations (CFR) | 싱크탱크 | 무료 | cfr.org | durable |
| CSIS | 싱크탱크 | 무료 | csis.org | durable |
| Carnegie Endowment | 싱크탱크 | 무료 | carnegieendowment.org | durable |
| Chatham House | 싱크탱크 | 무료 | chathamhouse.org | durable |
| Foreign Affairs | 저널 | 페이월(일부 무료) | foreignaffairs.com | durable |
| GZERO Media (Ian Bremmer) | 유튜브 | 무료 | @gzeromedia · UC-8_qAhNVG8G1wxONMnYr3Q | live |
| Zeihan on Geopolitics | 유튜브 | 무료 | @zeihanongeopolitics · UCsy9I56PY3IngCf_VGjunMQ | live(분석틀) |

보조 원자료: Brookings(brookings.edu), ECFR(ecfr.eu).

## 2. 국제금융·경제

| 소스 | 유형 | 접근 | URL / 채널 | 분류 |
|---|---|---|---|---|
| IMF | 국제기구 | 무료 | imf.org/en/Data · WEO 리포트 | durable |
| BIS (국제결제은행) | 국제기구 | 무료 | bis.org (/statistics, /quarterlyreviews) | durable |
| World Bank | 국제기구 | 무료 | data.worldbank.org · Global Economic Prospects | durable |
| OECD | 국제기구 | 무료 | data.oecd.org · Economic Outlook | durable |
| FRED (St. Louis Fed) | 데이터 | 무료 | fred.stlouisfed.org (80만+ 시계열) | live(데이터) |
| Financial Times | 신문 | 페이월 | ft.com | live |
| Patrick Boyle | 유튜브 | 무료 | @pboyle · UCASM0cgfkJxQ1ICmRilfHLw | durable(해설) |

1차 원자료: 미 연준(federalreserve.gov), ECB(ecb.europa.eu). 병행 매체: The Economist·WSJ(페이월).
※ FRED·World Bank·IMF·ECB·BIS는 이미 `hedge-quant-strategies/data/fetch_data.py`로 프로그램 조회 가능.

## 3. 국제경영·비즈니스

| 소스 | 유형 | 접근 | URL / 채널 | 분류 |
|---|---|---|---|---|
| Harvard Business Review | 웹/저널 | 미터드(일부 무료) | hbr.org | durable |
| McKinsey Global Institute | 컨설팅 리서치 | 무료(일부 등록) | mckinsey.com/mgi · /featured-insights | durable |
| BCG Publications | 컨설팅 | 무료 | bcg.com/publications | durable |
| Bain Insights | 컨설팅 | 무료 | bain.com/insights | durable |
| HBR (유튜브) | 유튜브 | 무료 | @harvardbusinessreview · UCWo4IA01TXzBeGJJKWHOG9g | durable |

보조: MIT Sloan Management Review(sloanreview.mit.edu, 미터드).

## 4. AI 최신 기능·활용법

| 소스 | 유형 | 접근 | URL / 채널 | 분류 |
|---|---|---|---|---|
| Anthropic | 공식 | 무료 | docs.anthropic.com · anthropic.com/news | durable+live |
| OpenAI | 공식 | 무료 | platform.openai.com/docs · openai.com/news | durable+live |
| Google DeepMind | 공식 | 무료 | deepmind.google/discover/blog · ai.google.dev | durable+live |
| The Batch (DeepLearning.AI) | 뉴스레터 | 무료 | deeplearning.ai/the-batch | live(주간) |
| Simon Willison | 블로그 | 무료 | simonwillison.net | durable+live |
| Two Minute Papers | 유튜브 | 무료 | @twominutepapers · UCbfYPyITQ-7l4upoX8nvctg | durable |
| Andrej Karpathy | 유튜브 | 무료 | @andrejkarpathy · UCXUPKJO5MZQN11PqgIvyuvQ | durable |
| AI Explained | 유튜브 | 무료 | @aiexplained-official · UCNJ1Ymd5yFuUPtn21xtRbbw | live+durable |
| Import AI (Jack Clark) | 뉴스레터 | 무료 | importai.substack.com | live |

보조(홍보성 유의): Matt Wolfe(@mreflow) — AI 툴 큐레이션, 제휴 성격 있어 참고만.

## 사용 규율

- **durable 소스**: skill-autoupdate 등록부에 오른 유튜브 채널(GZERO·Zeihan·HBR·AI Explained
  등)은 주간 루틴이 자막을 수집해 분석틀을 갱신. 기관 리포트는 필요 시 심층 조회.
- **live 소스**: "지금 상황"에는 저장본을 쓰지 말고 조회 시점에 실시간 fetch(WebSearch/
  Firecrawl 우선, 도구 없으면 live_brief.py). 결과에 **조회 시각**을 반드시 표기.
- 페이월 소스는 무료 요약·헤드라인까지만 자동 활용, 본문은 사용자 접근 필요 안내.
- 새 소스 추가는 사람이 신뢰성 검증 후 등록(과대광고·홍보·사기 차단).
