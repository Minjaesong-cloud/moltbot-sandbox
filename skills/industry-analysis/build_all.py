"""
전 산업 프로파일 일괄 생성 — /loop 없이 한 번에 96개 산업의 근거 프로파일을 만든다.

왜 loop보다 이게 나은가: 산업 목록이 고정(Damodaran 96개)이라 반복 폴링이 불필요하다.
한 번 돌면 industry_profiles.json에 전부 저장 → 어떤 산업을 분석할 때든 즉시 참조.
데이터가 갱신되면(연 1~2회) 다시 실행. "지어낸 인사이트"가 아니라 실측+프레임 결과만 저장.

/loop이 정당한 경우는 따로 있다(아래 LOOP_NOTE): 실제 섹터 전문가 자막을 주기적으로
수집·추가하는 것 — 그건 새 소스가 계속 생기므로 반복이 의미 있다.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from industry_profile import _screener, profile

OUT = os.path.join(os.path.dirname(__file__), 'industry_profiles.json')

LOOP_NOTE = """
/loop 사용 지침:
- ❌ "96개 산업 인사이트 알아서 찾아라"를 loop로 → 소스 없이 반복하면 지어낸 견해 양산.
     대신 이 스크립트 한 번(build_all)이 실측 프로파일을 전부 만든다.
- ✅ loop가 맞는 경우: 실존 섹터 전문가 채널이 새 영상을 올리는지 주기적으로 확인해
     자막을 수집·추가(hedge-quant-strategies 파이프라인). 새 소스가 계속 생기므로 반복 유의미.
"""


def main():
    s = _screener()
    profiles = {}
    skipped = []
    for ind in s.index:
        try:
            p = profile(ind)
            if 'error' in p or not p.get('신호'):
                skipped.append((ind, 'no signals')); continue
            profiles[ind] = {
                '기업수': p['기업수'],
                '실측': {k: v for k, v in p['실측'].items() if v},
                '신호': [{'항목': a, '판정': b, '근거': c} for a, b, c in p['신호']],
                '전문가렌즈': [{'전문가': w, '해석': v} for w, v in p['전문가_렌즈']],
            }
        except Exception as e:
            skipped.append((ind, str(e)[:60]))
    json.dump(profiles, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(f"생성: {len(profiles)}개 산업 프로파일 → {OUT}")
    if skipped:
        print(f"제외 {len(skipped)}개(데이터 부족, 은폐 안 함): "
              + ', '.join(f'{i}({r})' for i, r in skipped[:8]) + ('...' if len(skipped) > 8 else ''))
    # 요약: 가치창출 상위·경기순환 극단
    top_moat = sorted(profiles.items(),
                      key=lambda kv: next((float(s.loc[kv[0], 'ROE']) - float(s.loc[kv[0], 'WACC'])
                                           for _ in [0] if True), -9), reverse=True)[:5]
    print("\n가치창출(ROE−WACC) 상위 5 산업:")
    for ind, _ in top_moat:
        roe, wacc = float(s.loc[ind, 'ROE']), float(s.loc[ind, 'WACC'])
        print(f"  {ind}: ROE {roe:.0%} − WACC {wacc:.0%} = {roe-wacc:+.0%}p")


if __name__ == '__main__':
    main()
    print(LOOP_NOTE)
