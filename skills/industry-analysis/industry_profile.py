"""
산업 프로파일러 — 임의 산업의 실제 경제지표를 즉시 뽑아 분석 프레임에 얹는다.

근거(전부 실측·무료): Damodaran 96개 산업(마진·ROE·베타·자본비용·밸류에이션) +
필요 시 SEC frames(미국 개별사 집계). "전문가 인사이트를 지어내지" 않는다 —
실제 산업 숫자에 검증된 프레임(생애주기·자본집약도·사이클)과 우리가 이미 추출한
전문가 렌즈(Damodaran 밸류·Marks 사이클·Greenblatt 특수상황)를 적용할 뿐.

사용: profile('Semiconductor')  또는  python industry_profile.py 반도체
"""
import os, sys, difflib
import pandas as pd, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hedge-quant-strategies', 'data'))
from damodaran import industry_screener

# 자주 쓰는 한국어/약칭 → Damodaran 산업명
ALIAS = {
    '반도체': 'Semiconductor', '반도체장비': 'Semiconductor Equip', '자동차': 'Auto & Truck',
    '자동차부품': 'Auto Parts', '은행': 'Banks (Regional)', '제약': 'Drugs (Pharmaceutical)',
    '바이오': 'Drugs (Biotechnology)', '소프트웨어': 'Software (System & Application)',
    '게임': 'Software (Entertainment)', '화학': 'Chemical (Basic)', '철강': 'Steel',
    '건설': 'Construction Supplies', '통신': 'Telecom (Wireless)', '유통': 'Retail (General)',
    '항공': 'Air Transport', '해운': 'Shipbuilding & Marine', '보험': 'Insurance (General)',
    '증권': 'Brokerage & Investment Banking', '호텔': 'Hotel/Gaming', '식품': 'Food Processing',
    '정유': 'Oil/Gas (Integrated)', '2차전지': 'Green & Renewable Energy',
}


def _screener():
    if not hasattr(_screener, '_c'):
        _screener._c = industry_screener()
    return _screener._c


def find_industry(name):
    """한국어 별칭·부분일치·오타 허용으로 Damodaran 산업명 탐색."""
    s = _screener()
    if name in ALIAS: name = ALIAS[name]
    if name in s.index: return name
    hit = [i for i in s.index if name.lower() in i.lower()]
    if hit: return hit[0]
    close = difflib.get_close_matches(name, list(s.index), n=1, cutoff=0.5)
    return close[0] if close else None


def profile(name):
    """산업 실측 프로파일 + 시장 대비 위치 + 프레임 신호."""
    s = _screener()
    ind = find_industry(name)
    if ind is None:
        return {'error': f"'{name}' 산업을 못 찾음. 가능: {[i for i in s.index][:5]}..."}
    r = s.loc[ind]
    mkt = s.median(numeric_only=True)   # 전 산업 중앙값 = 시장 기준선

    def cmp(col):
        v, m = r.get(col), mkt.get(col)
        if pd.isna(v) or pd.isna(m): return None
        return round(float(v), 3), round(float(v / m), 2) if m else None

    beta = float(r.get('베타')) if pd.notna(r.get('베타')) else None
    roe = float(r.get('ROE')) if pd.notna(r.get('ROE')) else None
    wacc = float(r.get('WACC')) if pd.notna(r.get('WACC')) else None
    gm = float(r.get('매출총이익률')) if pd.notna(r.get('매출총이익률')) else None
    loss = float(r.get('적자기업비율')) if pd.notna(r.get('적자기업비율')) else None

    # 프레임 신호(실측 숫자 → 구조적 해석)
    signals = []
    if beta is not None:
        signals.append(('경기민감도', '높음(경기순환주)' if beta >= 1.2 else
                        '낮음(방어주)' if beta <= 0.8 else '중간', f"베타 {beta:.2f}"))
    if roe is not None and wacc is not None:
        spread = roe - wacc
        signals.append(('가치창출', '자본비용 초과(해자 가능)' if spread > 0.03 else
                        '자본비용 잠식(구조적 열위)' if spread < -0.02 else '자본비용 수준',
                        f"ROE {roe:.0%} vs WACC {wacc:.0%} → {spread:+.0%}p"))
    if gm is not None:
        signals.append(('마진 구조', '고마진(차별화·IP)' if gm >= 0.5 else
                        '저마진(원가경쟁)' if gm <= 0.25 else '중간마진', f"매출총이익률 {gm:.0%}"))
    if loss is not None and loss >= 0.3:
        signals.append(('생애주기', '성장·초기(적자기업 다수 → 생존편향 주의)', f"적자기업 {loss:.0%}"))

    return {
        '산업': ind, '기업수': int(r['기업수']) if pd.notna(r.get('기업수')) else None,
        '실측': {'PER': cmp('PER(현재)'), 'PBV': cmp('PBV'), 'ROE': cmp('ROE'),
                 '순이익률': cmp('순이익률'), '베타': cmp('베타'), 'WACC': cmp('WACC')},
        '신호': signals,
        '전문가_렌즈': expert_lenses(ind, r, roe, wacc, beta),
    }


def expert_lenses(ind, r, roe, wacc, beta):
    """이미 추출한 실제 전문가 프레임을 이 산업 숫자에 적용(references/framework.md 연동)."""
    L = []
    per = float(r.get('PER(현재)')) if pd.notna(r.get('PER(현재)')) else None
    pbv = float(r.get('PBV')) if pd.notna(r.get('PBV')) else None
    if roe is not None and pbv is not None:
        # Damodaran: PBV는 ROE로 정당화되는가 (PBV ≈ (ROE-g)/(CoE-g))
        L.append(('Damodaran(밸류)',
                  f"PBV {pbv:.1f} — ROE {roe:.0%}가 이 프리미엄을 정당화하는가. "
                  + ('ROE 높아 프리미엄 근거 있음' if roe and roe > 0.2 else
                     'ROE 낮은데 프리미엄 → 성장 기대 or 과열 의심')))
    if beta is not None:
        L.append(('Marks(사이클)',
                  f"베타 {beta:.2f} — {'경기순환 심함: 사이클 어디인지가 진입의 전부. 바닥 비관에서 사고 정점 낙관에서 판다' if beta >= 1.2 else '방어적: 사이클보다 개별 해자·규제가 관건'}"))
    if roe is not None and wacc is not None and roe - wacc < -0.02:
        L.append(('Greenblatt/Marks(구조)',
                  "자본비용 잠식 산업 → 평균회귀 베팅은 위험. '싸 보이는' 이유가 구조적일 수 있음"))
    L.append(('Dalio(매크로)',
              f"{'금리·경기에 민감(경기순환)' if beta and beta>=1.2 else '금리 민감도 낮음'} — 부채사이클·유동성 국면과 함께 볼 것"))
    return L


if __name__ == '__main__':
    q = sys.argv[1] if len(sys.argv) > 1 else 'Semiconductor'
    import json
    p = profile(q)
    if 'error' in p:
        print(p['error']); sys.exit(1)
    print(f"=== {p['산업']} ({p['기업수']}개사) ===")
    print("실측(값, 시장중앙값 대비 배율):")
    for k, v in p['실측'].items():
        if v: print(f"  {k:8s} {v[0]:>8}  ({v[1]}x 시장)")
    print("구조 신호:")
    for name, verdict, basis in p['신호']:
        print(f"  {name}: {verdict}  [{basis}]")
    print("전문가 렌즈:")
    for who, view in p['전문가_렌즈']:
        print(f"  {who}: {view}")
