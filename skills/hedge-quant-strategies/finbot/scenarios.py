"""
시나리오 분석 — "지금 이 포트폴리오가 과거 위기를 다시 만나면 얼마나 깨지는가"

두 포트폴리오를 스트레스 테스트한다:
  1. 자산배분 엔진의 현재 목표 비중 (strategy_engine)
  2. 가상 계좌의 현재 보유 종목 (sim_account.json)

방법: 실제 과거 위기 구간의 자산별 수익률을 그대로 현재 비중에 적용(역사적 시나리오).
예측이 아니라 "이 정도 충격은 언제든 다시 올 수 있다"는 노출 점검이다(Marks: 리스크 =
잃을 수 있는 금액). 상관관계 변화·유동성 경색은 반영 못 하므로 실제는 더 나쁠 수 있다.
"""
import os, sys, json
import pandas as pd, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from fetch_data import fred, naver_daily, blockchain_btc

EPISODES = {   # 이름: (시작, 끝)
    '2008 금융위기 (6개월)':  ('2008-09-01', '2009-03-09'),
    '2020 코로나 (5주)':      ('2020-02-19', '2020-03-23'),
    '2022 인플레 긴축 (1년)': ('2022-01-01', '2022-12-31'),
    '2018 Q4 급락':          ('2018-10-01', '2018-12-24'),
}


def _ret(series, s, e):
    x = series.loc[s:e].dropna()
    return float(x.iloc[-1] / x.iloc[0] - 1) if len(x) > 2 else np.nan


def asset_scenarios():
    """자산배분 엔진 현재 비중 × 위기 구간 실제 수익률."""
    from strategy_engine import target_portfolio
    today, port, _ = target_portfolio()
    w = dict(zip(port['자산'], port['목표비중']))
    src = {'US_EQ': fred('NASDAQCOM'), 'JP_EQ': fred('NIKKEI225'),
           'OIL': fred('DCOILWTICO'), 'KRW': -fred('DEXKOUS'),
           'KR_EQ': naver_daily('KOSPI')['close'], 'BTC': blockchain_btc(timespan='all')}
    dgs = fred('DGS10')
    rows = []
    for ep, (s, e) in EPISODES.items():
        total, detail = 0.0, {}
        for a, wt in w.items():
            if wt == 0: continue
            if a == 'BOND10':
                dy = _ret_yield = (dgs.loc[s:e].dropna().iloc[-1] - dgs.loc[s:e].dropna().iloc[0])
                r = -7.0 * dy / 100
            elif a == 'KRW':
                x = fred('DEXKOUS').loc[s:e].dropna(); r = -(x.iloc[-1]/x.iloc[0]-1)
            else:
                r = _ret(src[a], s, e)
            if np.isnan(r): continue
            total += wt * r; detail[a] = f"{r:+.0%}"
        rows.append({'시나리오': ep, '포트폴리오 손익': f"{total:+.1%}", '자산별': detail})
    return w, rows


def stock_scenarios():
    """가상 계좌 보유 종목 스트레스: KOSPI 급락 재현 + 모멘텀 크래시 + 반도체 집중."""
    p = os.path.join(os.path.dirname(__file__), 'sim_account.json')
    if not os.path.exists(p): return None
    acct = json.load(open(p))
    total = acct['valuations'][-1]['total'] if acct['valuations'] else acct['initial']
    pos_val = acct['valuations'][-1]['positions_value'] if acct['valuations'] else 0
    exposure = pos_val / total
    semis = sum(pp['qty'] * pp['avg_price'] for c, pp in acct['positions'].items()
                if pp['name'] in ('삼성전자', 'SK하이닉스', '삼성전기'))
    semi_pct = semis / total
    out = []
    for name, shock in [('KOSPI 추가 -20% (베타 1 가정)', -0.20),
                        ('2020 코로나식 -35%', -0.35),
                        ('모멘텀 크래시 (2009식: 주도주 -50%)', -0.50)]:
        out.append({'시나리오': name, '예상 손실': f"{exposure*shock*total:,.0f}원 ({exposure*shock:+.1%})"})
    return {'주식 노출': f"{exposure:.0%}", '반도체 3사 집중도': f"{semi_pct:.0%}", '시나리오': out}


if __name__ == '__main__':
    w, rows = asset_scenarios()
    print("=== 자산배분 엔진 현재 비중:", {k: v for k, v in w.items() if v > 0})
    for r in rows:
        print(f"  {r['시나리오']:22s} → {r['포트폴리오 손익']}  {r['자산별']}")
    s = stock_scenarios()
    if s:
        print(f"\n=== 가상 계좌 (주식 노출 {s['주식 노출']}, 반도체 집중 {s['반도체 3사 집중도']})")
        for r in s['시나리오']:
            print(f"  {r['시나리오']:32s} → {r['예상 손실']}")
    print("\n주의 1: 역사적 시나리오는 하한이 아니다. 상관 급등·유동성 경색 시 실제는 더 나쁠 수 있다.")
    print("주의 2: 이건 '오늘 비중을 고정'한 정적 충격이다. 실제 엔진은 추세 이탈 시 슬리브를 끄고")
    print("        FSI 게이트·볼타깃이 축소하므로 점진적 하락에선 이보다 작다(백테스트: 2008 추세 -8%).")
    print("        갭 하락(하루아침 급락)에는 방어가 못 따라간다 — 그게 이 표가 보여주는 리스크다.")
