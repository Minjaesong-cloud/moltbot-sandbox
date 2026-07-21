# 제조/생산 알고리즘 + idiot index + 공장이 제품

출처 공통: [Everyday Astronaut, Starbase Tour(2021)](https://everydayastronaut.com/starbase-tour-and-interview-with-elon-musk/);
Walter Isaacson, *Elon Musk*(2023, "The Algorithm" 챕터).

## The Algorithm — 5단계 (반드시 이 순서로)

가장 중요한 건 **순서**다. 자동화·최적화를 먼저 하는 것이 가장 흔한 실수.

1. **요구사항을 덜 멍청하게 (Make requirements less dumb)**
   > "The requirements are definitely dumb; it does not matter who gave them to you."

   특히 똑똑한 사람이 준 요구사항이 위험하다 — 덜 의심하게 되므로. 모든 요구사항에
   그것을 만든 사람의 이름을 붙여라(부서가 아니라 사람이 책임지도록).

2. **부품·공정을 삭제 (Delete the part or process)**
   > "If parts are not being added back into the design at least 10% of the time, you're not
   > deleting enough."

   되돌리는 비율이 10% 미만이면 충분히 안 지운 것. 즉 **일부러 과하게 지우고** 필요한
   것만 다시 넣는다.

3. **단순화·최적화 (Simplify and optimize)** — 반드시 1·2 이후에.

4. **사이클 타임 가속 (Accelerate cycle time)**
   > "You're moving too slowly, go faster! But don't go faster until you've worked on the
   > other three things first."

5. **자동화 (Automate)** — 맨 마지막. 문제를 진단한 뒤 불필요한 공정 내 검사를 제거.

### 가장 흔한 실수
> "The most common error of a smart engineer is to optimize a thing that should not exist."

존재하면 안 될 부품·공정을 열심히 최적화하는 것 — 순서(2단계 삭제)를 건너뛰면 벌어진다.

### 삭제의 미학
> "The best part is no part. The best process is no process. It weighs nothing, costs nothing,
> can't go wrong."

설계 회의에서 부품을 추가한 것이 아니라 **없앤 것(undesign)** 을 자랑할 때 가장 높이 산다.
`(2-4·2-5는 표현 재구성 가능성 — 취지 정확)`

### 생산이 설계보다 10~100배 어렵다
프로토타입 설계는 쉽고, 그것을 양산하는 **생산 시스템 구축**이 진짜 난제.
> "Developing the production system is 10 to 100 times harder than designing the product."
> `(표현 재구성 가능성)`

## Idiot Index (바보 지수)

**정의**: 완제품 원가 ÷ 그 원자재 상품가격. 비율이 높을수록 설계가 과도하게 복잡하거나
공정이 비효율적이라는 신호.

> "If the ratio [finished cost to raw-material cost] is high, you're an idiot."

- 예: 원가 $1,000짜리 부품의 알루미늄 값이 $100이면 idiot index = 10.
- 로켓의 idiot index는 ~50배였다 → SpaceX 창업의 정량 근거.
- **운영 적용**: 재무팀이 부품별 idiot index를 추적 → 지수 높은 것부터 원가 절감 공격.

출처: Walter Isaacson, *Elon Musk*(2023) —
[Secret CFO](https://www.linkedin.com/posts/secret-cfo_best-takeaway-from-the-new-elon-musk-book-activity-7127987898842279936-QGGM)

## 공장이 곧 제품 — "기계를 만드는 기계"

> "The factory is the machine that builds the machine." / "We consider the factory itself to
> be a product."

> "The biggest epiphany I had building Tesla is that what really matters is the machine that
> builds the machine — the factory."

- 장기 경쟁우위는 제품이 아니라 **제조(수직계열화)** 에서 나온다.
  > "Tesla's long-term competitive advantage will be manufacturing."
- 제1원리 물리 분석상 완성차 설계보다 **제조에서 5~10배** 개선 잠재력이 있다고 봄.

출처: Tesla 실적발표(2016~) — [Electrek](https://electrek.co/2016/06/01/elon-musk-machines-making-machines-rant-about-tesla-manufacturing/),
[CleanTechnica(2020)](https://cleantechnica.com/2020/08/21/elon-musk-teslas-long-term-competitive-advantage-will-be-manufacturing/)

## 적용법

- 무언가를 개선하기 전에 **순서**를 지켜라: 요구사항 의심 → 삭제 → 단순화 → 가속 → 자동화.
- "이걸 최적화하자" 전에 "이게 **존재해야 하나**"를 먼저 물어라.
- 원가 문제는 idiot index로 정량화 — 원자재 대비 배율 높은 것부터.
- 시스템(공장·프로세스) 개선이 개별 산출물 개선보다 레버리지가 크다.
