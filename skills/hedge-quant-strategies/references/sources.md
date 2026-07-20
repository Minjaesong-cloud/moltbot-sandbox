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

## 3. 추가 전문가 (허브 확장)

- **Ben Felix** (PWL Capital CIO, 유튜브 Common Sense Investing) — 영상 12편 자막 →
  `references/experts/ben-felix.md`. 증거 기반 팩터 투자·인덱스·행동재무학. 학술 논문
  (Fama-French, Bessembinder, Hartzmark & Solomon 등)을 실무로 번역.
- **Ray Dalio** (Bridgewater 창업자, 유튜브 Principles) — 영상 10편 자막(How the Economic
  Machine Works 1~5, Changing World Order, 부채 사이클 등) → `references/experts/ray-dalio.md`.
  매크로·부채 사이클·빅 사이클 프레임워크.
- **Aswath Damodaran** (NYU Stern, 유튜브 "Aswath Damodaran on Valuation") — Little Book of
  Valuation 시리즈 등 영상 13편 자막 → `references/experts/aswath-damodaran.md`. 가격 vs
  가치, DCF·멀티플, 스토리와 숫자, 생애주기별 밸류에이션(특히 부실기업), 통제가치. 가치·
  디스트레스트·이벤트드리븐·액티비스트 전략의 펀더멘털 근간.
- **Robert Carver** (전 Man AHL, 『Systematic Trading』 저자) — 강연 2편 자막
  ("Simplicity in Systematic Trading", "Diversification of Trading Strategies") →
  `references/experts/robert-carver.md`. 시스템 트레이딩 설계·과최적화·분산·포지션 사이징.
- **Howard Marks** (Oaktree Capital 창업자, 『The Most Important Thing』·『Mastering the
  Market Cycle』 저자) — 강연·대담 3편 자막 → `references/experts/howard-marks.md`. 2차적
  사고, 시장 사이클·심리, 리스크(영구 손실), 디스트레스트·크레딧, 역발상.
- 수집 방법: yt-dlp로 채널 영상 목록을 받아 전략·투자 관련 영상을 선별하고 자동 생성
  영어 자막(VTT)을 다운로드해 텍스트로 정리 후 인사이트 추출.
- 전문가 간 일치/차이는 SKILL.md의 "전문가 간 공통 원칙 vs 관점 차이" 섹션에 정리.

## 주의

- 자동 생성 자막이라 표기 오차가 있을 수 있으나, 인용문은 원 발언의 취지를 보존했다.
- 수치(수익률·수수료·스프레드 등)는 강의 시점·특정 사례의 예시다. 절대값이 아니라
  자릿수·구조를 이해하는 참고용으로 쓴다.
- Patrick Boyle의 관점은 회의적·실증 중심이다. 다른 전문가를 추가하면 관점이 갈릴 수
  있으며, 그 경우 SKILL.md의 허브 확장 가이드에 따라 "관점 차이"로 정리한다.
