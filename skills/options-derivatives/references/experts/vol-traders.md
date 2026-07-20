# 옵션·변동성 트레이딩 실무 — Euan Sinclair & Benn Eifert

Boyle의 그릭스·프라이싱 이론(options-greeks.md)을 **실전 트레이딩 관점**으로 보강.
- **Euan Sinclair**: 『Volatility Trading』·『Positional Option Trading』 저자, 전 옵션 마켓메이커.
- **Benn Eifert**: QVR Advisors 창업자, 변동성 전문 헤지펀드 매니저.

## 1. 변동성 리스크 프리미엄(VRP)

- **볼록성이 프리미엄을 낳는다**(Sinclair): 옵션은 무제한 상방+제한 하방 → 아무도 공정가치에
  안 판다. "convexity is begging for a risk premium." 그래서 IV > RV, 옵션 매도 = 이 프리미엄 수취.
- **VRP는 시간가변적**: 사라지는 구간도 있다("risk premia come and go"). 완전히 0은 안 됨
  (그러면 모두 공정가치에 사기만). **VRP는 10년 무수익 구간이 한 번도 없었다**(ERP는 3번) →
  트레이딩 피라미드의 가장 신뢰할 기반.
- **다변화 필수**: 채권·VIX·지수 등에 분산 수확. 단일 자산 집중 금지.
- **2020년 3월 구조 리셋**(Eifert): 분산 매도자가 25년 이익을 날리고 사라짐 → 테일/볼록성 가격
  영구 상향(VIX-ATM 프리미엄 2~3pt → 4~7pt). **VRP 수준은 매도자 공급이 결정한다.**

## 2. 옵션 트레이딩의 진짜 엣지

- **엣지 = 양의 기대값이 전부**(Sinclair): "비싸게 팔거나 싸게 사거나. 안 그러면 리스크관리·
  심리도 소용없다." 모든 것은 **"변동성이 너무 높은가 아닌가"** 하나로 귀결. 구조(콘도르냐
  버터플라이냐)는 부차적.
- **리테일이 실패하는 이유**: 매직 구조·매직 타이밍 집착("9:20에만 통하면 엣지가 아니라 운").
  비용이 엣지를 잡아먹음(0DTE는 오히려 더 잘해야). 손실 후 엉뚱한 조정(근본 리스크 팩터는 동일).
  비현실적 기대("하루 1%"=연 300%=Simons의 5배).
- **단순함 > 복잡함**: "내가 아는 좋은 트레이더는 다 단순한 걸 잘한다." 한 가지를 찾아 20년
  두들긴다. "80% 수준의 4~5개 > 95% 수준의 1개." 복잡·흥미로운 것은 "지적 호기심의 블랙홀".
- **레버리지드 베타 무시 말 것**: 대부분의 "알파"는 레버리지드 베타. "your bank account
  doesn't care if it's beta or alpha."
- **옵션 사용 문턱을 높게**(Eifert): 볼은 "일곱 번째로 생각할 것", 첫째는 payoff 프로파일·
  시간지평·상하방·시나리오 확률. 밈스톡엔 "공정 볼"이 없다 — payoff와 확률로만.

## 3. 숏 볼의 위험과 관리

- **분산은 극도로 음의 비대칭**(Eifert): P&L이 볼의 제곱 — "볼 10배면 손실 100배."
- **파멸 패턴**: "조용한 시장에서 프로가 테일을 몰래 팔아 조금 더 벌다가, 5~10년에 한 번
  터진다." 매니저가 몰래 테일 파는지 검증할 질문을 갖춰라.
- **숏볼 위험은 없앨 수 없다**(Sinclair): "음의 스큐 거래를 양의 스큐로 바꿀 수 없다 — 그
  리스크를 지는 대가로 돈을 받는 것이니까." 스톱으로 없애려 하면 되돌아올 승자까지 잘린다.
- **콜 매도가 실은 더 위험**(둘 다): "내 최대 손실은 항상 콜 쪽, 숏 콜에서 났다." 상방 폭등이
  더 위험. "콜 매도의 안심은 거짓 낙원."
- **사이징 매직 룰**(Sinclair): "맞으면 돈 될 만큼 크게, 틀려도 재앙은 아닐 만큼. 그 지점을
  못 찾으면 그 거래는 네 것이 아니다." 켈리 × 믿음 계수(0~10).
- **헤지는 스톱이 아니라 구조적으로**: 스톱은 "재앙 헤지"로만(분기 1회 발동 수준). "옵션을
  판다고 네이키드일 필요 없다 — 30년 팔고 안 터졌다." 집단 스톱(같은 시각·같은 가격)은 스톱
  헌팅 먹잇감.

## 4. 변동성 거래 실무

- **헤지는 "덜 과평가된" 옵션으로**(Sinclair): 자기가 판 것보다 더 비싼 걸로 헤지 마라. **달러가
  아니라 볼 기준 가장 덜 과평가된 것**(보통 장기 옵션). 숏 북 1주~1개월이면 헤지는 3~6개월,
  10델타 말고 **40델타 근처**(크래시에서 더 도움).
- **손실 없는 롱옵션 전략은 금**(Sinclair): "돈 안 잃는 롱옵션 전략을 찾으면 무조건 하라 —
  돈을 못 벌어도, 세상이 무너질 때 살아나니까." 예: 어닝 2주 전 매수→발표 후 매도.
- **VIX 풋 매도 = 방향성 롱 VIX**(Sinclair): 시장 붕괴 시 스파이크로 수익(숏볼 북 헤지), 평시
  theta 수취. "VIX가 19→10으로 하루에 안 떨어진다"(19→80은 가능) → 네이키드 숏 하방 걱정 적음.
- **딜러 감마 = 가속기**(Eifert): 감마는 방향이 아니라 **가격 움직임을 양방향으로 증폭**. 딜러를
  숏 감마로 미는 플로가 무브를 키운다.
- **디스퍼전**(Eifert, QVR 핵심): 인덱스 볼 vs 개별종목 볼 = 상관 노출. 2022년 기회 = 개별종목
  롱볼 + 인덱스 숏볼(개별은 어닝·로테이션으로 실현볼↑, 인덱스는 탈상관으로 조용).
- **실행 — "한쪽만 하는 마켓메이커"**(Eifert): 양쪽 호가를 안 내고, 살 것엔 best bid/팔 것엔
  best offer를 고빈도로 제시하며 mid 근처로 "chisel in". 대형 유동성 인출은 오늘날 불리(은행
  리스크 창고 능력 저하).
- **자동화는 필요할 때까지 하지 마라**(Sinclair): 너무 일찍 자동화하면 체결·역선택에서 배우는
  걸 잃는다. AI·자동화는 스프레드시트 같은 도구일 뿐.

## 5. 시장 구조 · 역사적 교훈

- **"낮다(low) ≠ 싸다(cheap)"**(Eifert): "과거보다 낮으니 싸다"는 틀렸다. **파생·변동성에서
  가장 중요한 원칙.** VIX 60·실현 15면 "돈 찍는 ATM"이라 매도로 눌린다.
- **VIX = 단기 내재변동성이지 공포지수 아니다**(Eifert). 장기 감각: 실현 16 → ATM 18 →
  분산스왑/VIX 20~21. "1.5% 매일 하락"이면 실현볼 ≈ 24 → "VIX 60"은 안 맞는다(볼 25~30만 넘어도
  매도가 압도). 반면 6개월 30% OTM 풋은 거의 공짜에 대박.
- **딜러 포지셔닝은 통념과 반대일 수 있다**(Eifert): "콜 오버라이팅 때문에 딜러는 늘 하방 숏
  감마"는 과단순화. OI로 감마 월을 추론하는 건 대부분 사후 합리화.
- **볼 스파이크는 바닥 신호가 아니다**(Eifert): 2020년 3월 볼 정점은 시장 저점 이틀 **전**,
  2008 볼 정점은 시장 저점(2009.3)보다 훨씬 앞. "VIX 70 와야 바닥"은 근거 없다.
- **매크로 vs 파생 디슬로케이션 구별**(Eifert): 스마트 매크로 플로를 "말도 안 되는 미스프라이싱"
  으로 오판하면 전멸(2012~13 Nikkei 스큐 역전 — 아베노믹스 콜 매수를 역행한 파생 트레이더들).
  price-insensitive 플로인지, 정보 있는 방향성 베팅인지 구별하라.

## 인용

> "You have to sell things for more than they're worth or buy them for less. If you don't, no risk management will help." (Sinclair)
> "There's no magic structure and no magic time. It all comes back to: is volatility too high or not?" (Sinclair)
> "You can't turn a negatively skewed trade into a positively skewed one — that's why the variance is there." (Sinclair)
> "The biggest losses I've ever had have been on the call side, being short calls." (Sinclair)
> "If you find a strategy buying options that doesn't lose money, do it — when the world goes to pieces, it kicks in. That thing is gold." (Sinclair)
> "The variance risk premium has never had a 10-year period where it didn't pay off." (Sinclair)
> "There's a difference between low and cheap — the most important thing in anything derivatives and volatility." (Eifert)
> "Variance is massively negatively asymmetric. In March 2020, variance sellers lost 25 years of gains." (Eifert)
> "In quiet markets, pros get sucked into selling tail risk... and once every 5-10 years they blow up spectacularly." (Eifert)
> "Gamma is not directional — it's an accelerant." (Eifert)
> "No evidence a big VIX spike tells you the market has bottomed." (Eifert)
