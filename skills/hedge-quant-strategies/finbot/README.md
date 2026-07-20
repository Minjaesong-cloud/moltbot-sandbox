# finbot 실행 모듈 — 백테스트로 검증된 것만 코드로

`backtests/`에서 검증된 신호를 라이브 실행하는 모듈들. 전부 무료·키 불필요 소스만 사용.
**교육·리서치용 페이퍼 포트폴리오** — 실주문 전 비용·세금·슬리피지·집행 모듈 필요.

## 1. `strategy_engine.py` — 자산배분 엔진 (톱다운)

7개 슬리브: US_EQ(나스닥) · KR_EQ(KOSPI 월별) · JP_EQ(닛케이) · BOND10(미10년) ·
OIL(WTI) · KRW(원화) · BTC(blockchain.info).

신호 위계 (각 층의 백테스트 근거는 `backtests/` 문서):
1. **추세(스위치)**: 10개월 이평 on/off — Shiller 152년·KOSPI·BTC 검증
2. **밸류에이션(예산)**: Damodaran 월간 내재 ERP vs 10년 평균 — 스위치 아님(CAPE 타이밍 실패 검증)
3. **포지셔닝(보조)**: COT 투기 z-score 극단 시 사이징 조정 (조회 실패 시 1.0 페일세이프)
4. **사이징**: 슬리브당 연 10% 변동성 타깃, 총 그로스 상한 2.0

주기 처리: 일별 자산 252(크립토 365)일 기준, 월별 자산(KOSPI)은 36개월 창·√12 연간화 —
월별 시리즈를 일별 인덱스에 섞으면 변동성이 왜곡되므로 자산별로 따로 계산한다.

라이브 실행 예 (2026-07-20): 주식 3슬리브 ON(합 1.21), BOND10·KRW·BTC OFF, 그로스 1.38.
내재 ERP 4.20% < 10년평균 4.97% → 주식 기대수익 예산 축소 신호(참고 정보).
**주의**: KR_EQ는 월별 데이터라 최대 7주 시차. BTC OFF 판정은 일별 최신.

## 2. `stock_screener.py` — 개별 종목 스크린 (보텀업)

SEC XBRL frames 5개 요청으로 **전 미국 상장사(~3,700개 교집합)** 단면 팩터:
- **밸류** E/P = 순이익/유통시총(EntityPublicFloat)
- **퀄리티** ROE = 순이익/자기자본
- **이익의 질** 발생액/자산 = (순이익−영업CF)/자산 → 최악 20% 제외 (Sloan 필터)

랭킹 = 밸류 백분위 + 퀄리티 백분위. 상위 후보에만 SIC 산업 개별 조회(요청 절약).

검증 근거 (`backtests/FUNDAMENTAL-FACTORS.md`): E/P 상위 18.2% vs 시장 13.0%,
ROE 상위 MaxDD −6.6%, 저발생액 15.6% vs 고발생액 12.8%.

**정직한 한계** (모듈 주석에도 명시):
- EntityPublicFloat는 내부자 지분 제외 → 내부자 지분 큰 기업의 E/P 과대. 가격도 Q2 말
  기준이라 최대 1년 낡음. **후보 발굴 스크린이지 트레이딩 신호가 아니다.**
- 통과 종목 심사 절차: ① `financial-statement-analysis` 스킬로 숫자의 질 검증 →
  ② `data/damodaran.py` 산업 스크리너로 산업 평균 대비 설명 안 되는 격차인지 확인.
- 2026-07 실행에서 확인된 전형적 왜곡: 초고 ROE(600%+)는 장부자본이 작은 산술 왜곡,
  초고 E/P(70%+)는 float 과소·가격 낡음 의심 — 극단값일수록 데이터부터 의심할 것.

## 데이터 의존성

| 모듈 | 소스 | 갱신 주기 |
|---|---|---|
| strategy_engine | FRED(지수·금리·FX), blockchain.info(BTC), CFTC(COT), Damodaran(내재 ERP) | 일/주/월 |
| stock_screener | SEC XBRL frames + submissions(SIC) | 분기(공시 후) |

전체 소스 목록·함정: `../data/ACCESSIBLE-DATA-INVENTORY.md`, `../data/DAMODARAN-SCREENER.md`.
