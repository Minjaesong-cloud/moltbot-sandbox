---
name: industry-analysis
description: 산업 분석 스킬. 임의의 산업(반도체·자동차·은행·제약·소프트웨어·화학·철강·통신·정유·바이오 등 국내외 모든 섹터)을 분석할 때, 그 산업의 실제 경제구조(마진·ROE·자본집약도·베타·밸류에이션)와 검증된 분석 프레임(생애주기·경기민감도·해자·사이클)과 이미 추출한 투자 전문가 렌즈(Damodaran 밸류·Marks 사이클·Dalio 매크로·Greenblatt 특수상황)를 즉시 적용합니다. 산업 리포트·섹터 분석·산업 비교·투자 유망 섹터 판단·개별 기업을 산업 맥락에서 볼 때 사용하세요. 사용자가 특정 산업·업종·섹터의 구조·전망·투자매력·경쟁강도·밸류에이션을 분석하거나 "이 산업 어때", "무슨 업종이 좋아", "섹터 분석" 등을 언급하면 반드시 참고하세요. 근거 없는 전문가 견해를 지어내지 않고 실측 데이터에 프레임을 적용하는 것이 원칙입니다.
---

# 산업 분석 — 실측 데이터 × 검증된 프레임 × 전문가 렌즈

임의의 산업을 **즉시 그 분야의 경제구조와 전문가 렌즈로** 분석하는 스킬. 자매 스킬
`hedge-quant-strategies`(전략·전문가 인사이트)와 `financial-statement-analysis`(개별사 숫자
검증)를 산업 층위에서 잇는다.

## ⚠️ 제1원칙 — 지어내지 않는다

이 스킬은 **"산업 X의 전문가는 이렇게 말한다"는 견해를 생성하지 않는다.** 대신:
- **실측 데이터**(Damodaran 96산업 마진·ROE·베타·자본비용·밸류에이션 + SEC 실제 재무)에
- **검증된 분석 프레임**(생애주기·경기민감도·해자·Porter)과
- **이미 실제 소스에서 추출한 전문가 프레임**(Damodaran·Marks·Dalio·Greenblatt — `hedge-quant-strategies/references/experts/`)을 적용한다.

즉 "반도체 전문가가 이렇게 본다"가 아니라 "반도체의 실제 ROE 31%·베타 1.52·PBV 13에
Damodaran의 밸류 규율과 Marks의 사이클 렌즈를 적용하면 이렇게 읽힌다"이다. 진짜 섹터
전문가(특정 애널리스트·유튜버)의 인사이트가 필요하면 `hedge-quant-strategies`의 방식대로
**실제 자막을 수집해** 추가한다(아래 "확장").

## 즉시 실행

```bash
python3 industry_profile.py 반도체      # 한국어 별칭·부분일치·오타 허용
python3 industry_profile.py "Auto & Truck"
```

출력: 실측 지표(값 + 시장 중앙값 대비 배율) → 구조 신호(경기민감도·가치창출·마진·생애주기)
→ 전문가 렌즈(Damodaran·Marks·Dalio가 이 숫자를 어떻게 읽는가).

## 라우팅

- 산업 실측 프로파일 + 전문가 렌즈 → `industry_profile.py`
- 분석 프레임(무엇을 보는가·전문가 렌즈 적용법·데이터 함정) → `references/framework.md`
- 워크드 예제(반도체 전체 분석) → `references/worked-semiconductor.md`
- 개별 기업을 산업 대비로 → `hedge-quant-strategies/data/damodaran.py`(상대가치 스크리너)
- 개별사 숫자의 질 검증 → `financial-statement-analysis` 스킬
- 사이클·매크로 국면 → `hedge-quant-strategies/references/experts/`(Marks·Dalio·Druckenmiller)

## 표준 워크플로 (산업 하나 분석)

1. **실측 프로파일** — `industry_profile.py <산업>`로 경제구조 파악(1초).
2. **구조 판정** — 경기순환 vs 방어, 자본비용 초과 vs 잠식, 고마진 vs 원가경쟁, 생애주기.
3. **전문가 렌즈 적용** — Damodaran(멀티플이 ROE로 정당화되나) · Marks(사이클 어디인가) ·
   Dalio(매크로 민감도) · Greenblatt(구조적 열위 산업의 함정).
4. **개별사로 좁히기** — 유망하면 SEC frames·DART로 산업 내 종목을 스크린(자매 스킬).
5. **함정 점검** — 금융업 매출총이익률·적자기업 생존편향·음의 장부가 등(framework.md).

## 확장 — 진짜 섹터 전문가 추가하기 (선택)

특정 산업에 대해 실존 전문가(예: 반도체 애널리스트 유튜버)의 인사이트가 필요하면,
`hedge-quant-strategies`의 파이프라인을 그대로 쓴다: 실제 채널 자막 수집 → 서브에이전트
추출 → `references/experts/<이름>.md`. **실제 소스가 있을 때만** 추가한다 — 없으면
프레임+실측으로 충분하며, 지어낸 견해로 채우지 않는다.
