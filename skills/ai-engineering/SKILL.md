---
name: ai-engineering
description: AI·머신러닝 엔지니어링 스킬. LLM·신경망·트랜스포머·프롬프트 엔지니어링·모델 학습/파인튜닝·AI 시스템 설계·최신 AI 연구 동향을 다룹니다. AI 애플리케이션을 만들거나, LLM/에이전트를 설계하거나, 모델 선택·프롬프트·RAG·파인튜닝을 논의하거나, 최신 AI 논문·기법을 이해할 때 사용하세요. 사용자가 AI·LLM·머신러닝·신경망·모델 학습·프롬프트·에이전트 등을 언급하면 참고하세요. 이 스킬은 검증된 전문가(Karpathy·3Blue1Brown 등)의 실제 콘텐츠에서 추출한 인사이트로 skill-autoupdate가 지속 갱신합니다.
---

# AI 엔지니어링

AI·ML 시스템 설계와 최신 연구 동향 스킬. `skill-autoupdate` 시스템이 검증된 AI 전문가
채널의 새 콘텐츠에서 인사이트를 추출해 이 스킬을 지속 갱신한다.

## ⚠️ 상태

이 스킬은 **뼈대**다. 내용(references/)은 `skill-autoupdate`가 아래 신뢰 소스의 실제
자막을 수집·추출하면서 채워진다. **지어낸 내용 없음** — 실제 소스에서만 추출한다.

## 신뢰 소스 (sources_registry.json에서 검증됨)

| 전문가 | 채널 | 강점 |
|---|---|---|
| Andrej Karpathy | @AndrejKarpathy | ex-Tesla/OpenAI, LLM·신경망 실전(밑바닥부터) |
| 3Blue1Brown | @3blue1brown | 신경망·트랜스포머 수학 직관 시각화 |
| Two Minute Papers | @TwoMinutePapers | 최신 AI 논문 요약·추적 |
| Yannic Kilcher | @YannicKilcher | ML 논문 심층 리뷰 |
| Lex Fridman | @lexfridman | AI 연구자 심층 대담(원 논문 인용 유의) |

## 라우팅 (채워지는 대로)

- LLM·에이전트 설계 실무 → `references/llm-engineering.md` (예정)
- 신경망·트랜스포머 원리 → `references/foundations.md` (예정)
- 최신 연구 동향 → `references/research-updates.md` (예정, skill-autoupdate가 갱신)

## Anthropic/Claude 관련

Claude API·Claude Code·모델 선택 등 Anthropic 제품 질문은 전용 스킬/문서(`claude-api`,
`claude-code-guide`)를 우선 참조. 이 스킬은 일반 AI 엔지니어링·연구 동향을 다룬다.

## 갱신 방식

`skill-autoupdate`가 주기적으로 위 채널의 새 영상 자막을 수집 → 서브에이전트가 인사이트
추출 → 이 스킬 references에 출처와 함께 반영. 상충하는 관점은 병기(허브 구조).
