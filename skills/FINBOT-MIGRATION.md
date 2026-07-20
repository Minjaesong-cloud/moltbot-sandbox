# finbot 프로젝트 이식 가이드

이 저장소(moltbot-sandbox, **public**)에서 만든 투자 시스템 전체를 finbot 프로젝트로 옮기는
방법. 아래 프롬프트 한 개를 **finbot 프로젝트의 Claude Code 세션에 붙여넣으면 끝**.

## finbot 세션에 붙여넣을 프롬프트

```
https://github.com/Minjaesong-cloud/moltbot-sandbox 의 claude/uiux-design-skills-djjp6w
브랜치를 클론해서 다음을 이 프로젝트에 통합해줘:

1. skills/hedge-quant-strategies/ 폴더 전체 (전략 허브 + data/ + backtests/ + finbot/)
2. skills/options-derivatives/, skills/financial-statement-analysis/,
   skills/INVESTING-SKILLS-INDEX.md (자매 스킬)
3. skills/FINBOT-MIGRATION.md 의 "이식 후 할 일" 섹션을 따라 마무리해줘

통합 위치는 이 프로젝트 구조에 맞게 정하되, hedge-quant-strategies 내부의 상대경로
(data/ ↔ finbot/ ↔ backtests/)는 유지해줘. 스킬로 등록해서 투자 관련 작업에서 자동으로
참조되게 해줘.
```

## 무엇이 옮겨지는가 (전부)

- **데이터 계층** (`data/`): fetch_data.py — 무료 소스 30여 개(FRED·SEC frames·CFTC·CBOE·
  OFR·Naver 한국 일별·Ken French·Shiller 등) + 키 API(ECOS·Tiingo·Finnhub·EIA) +
  dart.py(한국 재무) + damodaran.py(산업 스크리너·국가 ERP·월간 내재 ERP) + 소스
  인벤토리/함정 문서 2종
- **전략 지식** (SKILL.md + `references/`): 8대 전략 패밀리 55개 전략, 전문가 8명 인사이트,
  실패 사례, 스큐 지도
- **백테스트 근거** (`backtests/`): 문서 10종 + 재현 스크립트 5종 — 자산배분·미국 팩터·
  한국 일별/팩터·변동성 신호·세금 분석. 유효/무효 판정 전부 포함
- **실행 엔진** (`finbot/`): strategy_engine(자산배분 7슬리브) · kr_stock_engine(한국 듀얼
  모멘텀+발생액 필터) · stock_screener(미국 전 상장사) · candidate_report ·
  sim_broker/sim_trade(가상 1천만원 매매, 논지 기록, S&P 벤치마크) · scenarios(위기 스트레스)
  · paper_log · kis.py(한투 클라이언트 — finbot 환경에서 검증)

## 이식 후 할 일 (finbot 세션에서)

1. **키 파일 재생성** (git에 없음 — 사용자가 내용 제공):
   - `data/.dart_key` — DART 키 한 줄
   - `data/.api_keys.json` — ecos/tiingo/finnhub/eia + kis_appkey/kis_appsecret/
     kis_account/kis_mode. **.gitignore에 두 파일 추가 필수**
2. **KIS 검증**: finbot 환경은 포트 제한이 없을 것 → `python3 finbot/kis_verify.py`
   (모의투자 5단계 검증). 통과하면 sim_trade의 가상 체결을 KIS 모의 주문으로 대체 가능
3. **주간 루틴 등록**: paper_log + kr_stock_engine + sim_trade(월초 리밸런스/그 외 평가) +
   scenarios 주 1회 실행·기록 커밋 (moltbot-sandbox의 루틴과 동일 사양 — 이식 후
   moltbot-sandbox 쪽 루틴은 꺼도 됨)
4. **가상 계좌 이어받기**: `finbot/sim_account.json`(2026-07-20 개시, 5종목 보유)을 그대로
   가져가면 기록 연속성 유지

## 사용자 목표 (finbot 쪽 Claude가 알아야 할 것)

- **S&P500 초과수익 + 변동성 최소화**가 목표. 매 평가에 S&P·KOSPI를 같이 기록 중
  (sim_broker.vs_benchmark)
- **감정 배제**: 모든 매수에 근거+무효화 조건("이게 깨지면 판다")을 기록하고, 매도는
  그 조건이 깨졌을 때만(sim_account.json의 theses). 사람이 개입해 임의 매도하지 않는 구조
- 절대 수치보다 검증된 상대 우위를 믿는다: 백테스트 문서의 "정직한 한계" 섹션들이
  이 시스템의 핵심 — 옮긴 뒤에도 그 규율(과최적화 금지·부정적 결과 기록)을 유지할 것
