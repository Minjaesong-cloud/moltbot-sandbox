# 출처 및 수집 방법

이 스킬은 두 종류의 소스를 결합한다:

## 1. 확립된 학술·업계 프레임워크 (기반)

`references/factor-investing.md`와 SKILL.md의 전략 분류·평가 프레임은 특정 개인의 발언이
아니라 표준화된 지식이다. 근거 문헌:
- Fama & French 3/5팩터 모델
- AQR (Cliff Asness) 팩터 연구
- Antti Ilmanen "Expected Returns", Andrew Ang "Asset Management"
- Marcos López de Prado "Advances in Financial Machine Learning" (퀀트 백테스트·과최적화)
- 헤지펀드 전략 분류(이벤트 드리븐/상대가치/매크로 등)는 업계 표준 분류(HFR 등)

## 2. Patrick Boyle 강의 시리즈 (실무 전문가 보강)

전직 헤지펀드 매니저이자 교수인 **Patrick Boyle**(유튜브 채널
https://www.youtube.com/@PatrickBoyleOnFinance, 채널 ID `UCASM0cgfkJxQ1ICmRilfHLw`)의
강의 영상 자막을 수집·분석했다.

- 수집 영상(11편, 약 47만 자): Applied Portfolio Management 시리즈(Class 2 자산군,
  Class 3 주식운용, Class 5 행동재무학, Class 7 헤지펀드 전략), How Hedge Funds Invest,
  Merger Arbitrage, Short Selling, PE/LBO/VC, Risk Parity Funds, Quant Trading History,
  What is a Quant Trader, GARCH/변동성.
- 수집 방법: yt-dlp로 채널 영상 목록(400편)을 받아 전략 관련 영상을 선별하고, 자동 생성
  영어 자막(VTT)을 다운로드해 텍스트로 정리했다.
- 추출 결과 → `references/hedge-fund-strategies.md`, `references/quant-strategies.md`,
  `references/boyle-quotes.md`.

## 주의

- 자동 생성 자막이라 표기 오차가 있을 수 있으나, 인용문은 원 발언의 취지를 보존했다.
- 수치(수익률·수수료·스프레드 등)는 강의 시점·특정 사례의 예시다. 절대값이 아니라
  자릿수·구조를 이해하는 참고용으로 쓴다.
- Patrick Boyle의 관점은 회의적·실증 중심이다. 다른 전문가를 추가하면 관점이 갈릴 수
  있으며, 그 경우 SKILL.md의 허브 확장 가이드에 따라 "관점 차이"로 정리한다.
