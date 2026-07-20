---
name: skill-autoupdate
description: 스킬 자동 갱신 시스템. 신뢰할 수 있는 전문가(유튜브 채널 allowlist)의 새 콘텐츠를 주기적으로 감지·수집해 관련 스킬(투자·산업·디자인·AI)을 최신 인사이트로 갱신합니다. 산업·시장·기술처럼 실시간으로 바뀌는 분야의 전문가 지식을 계속 최신화하고 싶을 때, 신뢰 소스 등록부를 관리하거나 새 전문가를 추가하거나 스킬 갱신 파이프라인을 돌릴 때 사용하세요. 사용자가 "최신 정보로 갱신", "새 전문가 추가", "스킬 최신화", "전문가 채널 추적" 등을 언급하면 참고하세요. 핵심 원칙: 인기가 아니라 신뢰 기준으로 검증된 소스만 수집하며, 근거 없는 정보를 지어내지 않습니다.
---

# 스킬 자동 갱신 — 신뢰 소스만, 지속 최신화

산업·시장·기술은 실시간으로 바뀐다. 검증된 전문가의 새 콘텐츠를 주기적으로 수집해
관련 스킬을 최신화하되, **오염을 막는 규율**을 지킨다.

## ⚠️ 제1원칙 — 인기 ≠ 신뢰 (가장 중요)

"전부 뒤져서 뜨는 걸 믿는다"는 **금지.** X·유튜브에서 인기 있는 것을 무차별 흡수하면
스킬이 과대광고·펌프앤덤프·사기·지어낸 소리로 오염된다 — 좋은 선택의 정반대. 이 시스템은:
- **`sources_registry.json`의 allowlist만 수집.** 검증된 실존 전문가(Damodaran·Boyle·
  Karpathy·마디아 등)만. 새 소스 추가는 사람이 검증 후 등록.
- **근거 없는 견해를 생성하지 않는다.** 실제 자막(원 소스)에서만 추출, 출처 기록.

## 무엇이 되고 안 되는가 (이 환경에서 실측)

| 소스 | 상태 | 방법 |
|---|---|---|
| 유튜브 새 영상 감지 | ✅ 확실 | 채널 RSS(`feeds/videos.xml?channel_id=`) |
| 유튜브 자막 수집 | ⚠️ 됨(인내) | yt-dlp — 429 봇차단 잦음, 재시도 파도로 회복 |
| **X/트위터/SNS** | ❌ **불가** | 무료 API 폐지·nitter 사망·JS 월. **자동 수집 불가** |

→ X 신뢰 계정(예: @naval, @karpathy)의 콘텐츠는 **사용자가 직접 붙여넣으면** 반영한다.
자동 크롤링은 하지 않는다(신뢰·법적 리스크 + 기술적 불가).

## 파이프라인

```bash
python skill_refresh.py --resolve   # 1. 신뢰 채널 RSS → 새 영상 감지 → harvest_queue.json
python harvest.py --max 20          # 2. 새 영상 자막 수집(yt-dlp 재시도 파도) → transcripts/
# 3. 루틴의 Claude가 transcripts/ 새 자막에서 인사이트 추출 → 대상 스킬 references 갱신(출처 기록)
# 4. 커밋·푸시
```

## 라우팅

- 신뢰 소스 등록부(도메인별 전문가 allowlist) → `sources_registry.json`
- 새 영상 감지 → `skill_refresh.py`
- 자막 수집 → `harvest.py`
- 상태(마지막 확인 시각) → `refresh_state.json`, 수집 큐 → `harvest_queue.json`

## 도메인 → 대상 스킬

| 도메인 | 신뢰 소스(현재) | 갱신 대상 스킬 |
|---|---|---|
| investing | Patrick Boyle, Ben Felix, Damodaran | `hedge-quant-strategies` |
| industry | (investing 전문가 공유) | `industry-analysis` |
| design | 마디아(Madia) | `madia-uiux-design` |
| ai | Karpathy, Two Minute Papers, 3Blue1Brown, Yannic Kilcher, Lex Fridman | `ai-engineering` |

## 새 전문가 추가 절차 (사람이 검증)

1. 실존·신뢰 확인(실적·소속·평판 — 인기 아님).
2. `sources_registry.json`에 도메인·핸들 추가(channel_id는 refresh --resolve가 채움).
3. 다음 갱신부터 자동 추적. 대상 스킬이 없으면 스킬 뼈대부터 생성.

## 갱신 시 규율 (오염 방지)

- 추출한 인사이트마다 **출처(영상 제목·날짜·채널)** 를 references에 기록.
- 기존 전문가와 **상충하면 "관점 차이"로 병기**(허브 구조 — hedge-quant-strategies 방식).
- 자막 자동생성 오차 감안, 수치는 자릿수·구조 참고용(원 발언 취지 보존).
- 새 정보가 기존 검증(백테스트 등)과 충돌하면 **덮어쓰지 말고** 대조·기록.
