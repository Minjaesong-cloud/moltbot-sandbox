# 실제로 뚫리는 무료 데이터 인벤토리 (검증됨)

이 리서치 환경(및 대부분의 제약 없는 finbot 환경)에서 **키 없이 실제로 수집 확인된** 무료
데이터 소스. 각 항목: 무엇 / 엔드포인트 / 커버리지 / 응용 전략. 수집 코드는 `fetch_data.py`.

> 확인 방법: 각 엔드포인트를 실제 호출해 데이터 반환을 검증(2026-07). SEC는 User-Agent 헤더
> 필수. rate limit 준수(GDELT 5초당 1, CoinGecko·SEC 과도호출 금지).

## ✅ 작동 확인된 소스

### 시장·매크로 — FRED (연준)
- `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`
- 커버리지: 미국·글로벌 금리(DGS2/10/30), FX(DEXKOUS 원화·DEXJPUS 엔·DEXUSEU), 원자재
  (DCOILWTICO·DCOILBRENTEU·DHHNGSP), 지수(SP500·NASDAQCOM·NIKKEI225·DJIA), OECD 각국 주가
  (SPASTT01KRM661N 한국 월간), 회사채(DAAA·DBAA), VIX(VIXCLS), 매크로(CPI·실업·GDP·M2·연준
  대차대조표) 수천 시리즈. **무료·무제한·키 불필요.**
- 전략: 추세추종·리스크패리티·매크로·캐리·자산배분. (backtests/ 결과가 이 데이터 기반.)

### 미국 펀더멘털·공시 — SEC EDGAR ★
- 티커맵 `https://www.sec.gov/files/company_tickers.json`
- 특정 항목 `https://data.sec.gov/api/xbrl/companyconcept/CIK<10자리>/us-gaap/<Tag>.json`
- 전체 재무 `https://data.sec.gov/api/xbrl/companyfacts/CIK<10자리>.json`
- 공시목록(10-K·8-K·13F) `https://data.sec.gov/submissions/CIK<10자리>.json`
- 커버리지: 미국 전 상장사 XBRL 재무(매출·순이익·자산·부채·현금흐름 등 전 항목, 분기·연간).
- 전략: **밸류·퀄리티 팩터, DCF, 이익의 질·M-score 분식탐지**(financial-statement-analysis
  스킬을 실제 재무로!), 13F로 기관 포지셔닝.

### 포지셔닝 — CFTC COT
- `https://publicreporting.cftc.gov/resource/6dca-aqww.json?$limit=<N>`
- 커버리지: 선물시장 투기·상업·딜러 주간 포지션(농산물·에너지·금리·FX·지수).
- 전략: 매크로·추세의 과열/청산 신호, 캐리 혼잡도.

### 암호화폐 — CoinGecko / Coinbase
- CoinGecko 시계열 `https://api.coingecko.com/api/v3/coins/<id>/market_chart?vs_currency=usd&days=<N>`
- Coinbase OHLCV `https://api.exchange.coinbase.com/products/<PROD>/candles?granularity=86400`
- (Binance는 이 환경에서 지역 차단. Coinbase·CoinGecko로 대체.)
- 전략: 크립토 추세·베이시스·펀딩·마켓메이킹(crypto-digital-asset.md).

### 글로벌 매크로 — IMF / World Bank
- IMF `https://www.imf.org/external/datamapper/api/v1/<indicator>/<country>` (예 NGDP_RPCH/KOR)
- World Bank `https://api.worldbank.org/v2/country/<iso2>/indicator/<code>?format=json`
- 전략: 국가 매크로·이머징·자산배분.

### 환율(유로 기준 장기) — ECB
- `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.csv` (전 통화 일별 1999~)

### 개별 주가 패널·심볼 — GitHub 공개 데이터셋
- S&P500 개별종목 `https://raw.githubusercontent.com/plotly/datasets/master/all_stocks_5yr.csv`
  (505종목 일별 2013-2018). 나스닥 심볼 목록, 각종 데이터셋.
- 전략: 종목 레벨 모멘텀·로우볼·리버설·페어(backtests/STOCK-LEVEL.md).

### 뉴스·이벤트(대체데이터) — GDELT
- `https://api.gdeltproject.org/api/v2/doc/doc?query=<q>&mode=timelinevol&format=json&timespan=7d`
- 전 세계 뉴스 볼륨·톤·이벤트. **5초당 1요청 제한.** 전략: 뉴스 감성·이벤트 탐지.

### 참고 — 에너지(EIA, 무료 키), 메타(Wikipedia API), 한국(pykrx·DART, 무료 키)
- GDELT rate limit 주의: 위반 시 **장시간 429**(경험적으로 수십 분). 반드시 5초/1요청.
- EIA `https://api.eia.gov/v2/...?api_key=<KEY>`(무료 발급), Wikipedia API, 한국 종목은 pykrx·
  OpenDartReader(korea-quant-resources.md).


### 팩터 정전 — Ken French Data Library ★신규 검증
- `https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/<DATASET>_CSV.zip`
- 3팩터(1926~)·5팩터(1963~)·모멘텀·산업포트폴리오 등. **팩터 연구의 표준.**
- 전략: 팩터 프리미엄 장기 검증·레짐 분석·팩터 타이밍(backtests/FUNDAMENTAL-FACTORS.md).

### SEC Frames — 전 기업 단면 재무 ★신규 검증 (팩터 구축의 핵심)
- `https://data.sec.gov/api/xbrl/frames/us-gaap/<Tag>/USD/CY<년>[Q4I].json`
- **한 요청으로 7,000+ 기업**의 특정 재무항목(NI·자기자본·CFO·자산). dei 주식수도 지원.
- 전략: 밸류(E/P)·퀄리티(ROE)·발생액 팩터를 실제 재무로 구축(검증 완료).

### 장기 밸류에이션 — Shiller / Damodaran ★신규 검증
- Shiller CAPE·금리·배당(1871~): `http://www.econ.yale.edu/~shiller/data/ie_data.xls`
- Damodaran 산업 멀티플·ERP·베타: `https://pages.stern.nyu.edu/~adamodar/pc/datasets/*.xls`
- 전략: 장기 밸류에이션 레짐, 산업 상대가치, ERP 추정(Damodaran 스킬과 연동).
- **파서/스크리너 구현 완료** → `damodaran.py` + `DAMODARAN-SCREENER.md` (96개 산업 대조표,
  한국 ERP 4.87% 파싱 검증. 함정: 음의 장부가 → PBV 극단값, 헤더 행 위치 매년 변동).

### 심리·크립토 보강 ★신규 검증
- 크립토 공포탐욕지수(2018~ 일별): `https://api.alternative.me/fng/?limit=0&format=json`
- Blockchain.info BTC 차트: `https://api.blockchain.info/charts/market-price?timespan=5years&format=json`
- 전략: 크립토 역발상·리스크 게이트.

### 기타 ★신규 검증
- BIS 실질실효환율(국가별 일별): `https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/D.N.B.KR?format=csv`
- NOAA 날씨(관측소 일별): `https://www.ncei.noaa.gov/access/services/data/v1?...` (농산물·에너지)
- NasdaqTrader 상장 심볼: `https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt`

## ❌ 이 환경에서 막힌 소스 (finbot 환경에선 될 수 있음)
- Yahoo Finance(yfinance/chart API — SSL 리셋·rate limit), stooq(JS 챌린지), Binance(지역 차단),
  FMP·Tiingo·Alpha Vantage(무료 키 필요, demo만 제한적).

## 수집기 사용법 (`fetch_data.py`)
```python
from fetch_data import fred, sec_ticker_map, sec_concept, cftc_cot, coingecko_market_chart, imf, github_sp500
y10 = fred('DGS10')                      # 미 10년 금리
cik = sec_ticker_map()['AAPL']           # 티커->CIK
rev = sec_concept(cik, 'Revenues')       # 애플 매출 시계열
ni  = sec_concept(cik, 'NetIncomeLoss')  # 순이익
cot = cftc_cot(2000)                     # CFTC 포지셔닝
btc = coingecko_market_chart('bitcoin', 365)
kr_gdp = imf('NGDP_RPCH', 'KOR')         # 한국 실질GDP성장
px = github_sp500()                       # S&P500 개별종목 패널
```

## finbot 데이터 파이프라인 권장 구성
1. **매크로·시장 코어**: FRED(자산군·금리·FX·원자재·유동성) — 추세추종·리스크패리티·매크로.
2. **미국 펀더멘털**: SEC EDGAR(밸류·퀄리티·M-score) — 종목 팩터·품질 필터.
3. **한국**: pykrx(시세·PER/PBR) + DART(재무) + 증권사 API(주문) — korea-quant-resources.md.
4. **포지셔닝·크립토·매크로 보강**: CFTC COT, CoinGecko/Coinbase, IMF/World Bank.
5. **대체데이터(선택)**: GDELT 뉴스, 이후 위성·카드·웹 등 유료로 확장(감쇠·적법성 유의).
6. **레퍼런스 필수**: 구성종목 이력·기업행위·상폐로 생존편향·룩어헤드 제거.
