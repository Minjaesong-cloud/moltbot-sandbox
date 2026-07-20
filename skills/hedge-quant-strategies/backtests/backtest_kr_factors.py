"""한국 재무 팩터 백테스트 (재현 스크립트) — DART 재무 × Naver 수정주가

결과 문서: KOREA-FUNDAMENTALS.md. DART 키 필요(data/.dart_key 또는 DART_API_KEY).
형성: FY t 사업보고서(3월 공시) → t+1년 6월 말, 12개월 보유, 동일가중 상위 5.
첫 실행 시 ~264 API 호출(병렬 6워커, 수 분). 캐시: ~/.cache/dart/kr_factor_panel.pkl
"""
import os, sys
import pandas as pd, numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from dart import corp_codes, annual_financials, total_shares, _CACHE
from fetch_data import naver_daily

UNIV = {'005930':'삼성전자','000660':'SK하이닉스','005380':'현대차','000270':'기아','005490':'POSCO',
'051910':'LG화학','035420':'네이버','017670':'SKT','030200':'KT','015760':'한전','055550':'신한지주',
'034730':'SK','003550':'LG','000810':'삼성화재','009150':'삼성전기','010130':'고려아연',
'004020':'현대제철','066570':'LG전자','012330':'현대모비스','006400':'삼성SDI','068270':'셀트리온',
'035720':'카카오','032830':'삼성생명','086790':'하나금융'}
YEARS = range(2015, 2026)


def harvest():
    p = os.path.join(_CACHE, 'kr_factor_panel.pkl')
    if os.path.exists(p):
        return pd.read_pickle(p)
    cmap = corp_codes()
    def one(args):
        stock, year = args
        f = annual_financials(cmap[stock][0], year)
        return dict(stock=stock, year=year, **f) if f else None
    rows = []
    with ThreadPoolExecutor(6) as ex:
        for fu in as_completed([ex.submit(one, (s, y)) for s in UNIV for y in YEARS]):
            r = fu.result()
            if r: rows.append(r)
    shr = {s: total_shares(cmap[s][0]) for s in UNIV}
    df = pd.DataFrame(rows)
    df['shares'] = df['stock'].map(shr)
    df.to_pickle(p)
    return df


def main():
    fin = harvest()
    fin['name'] = fin['stock'].map(UNIV)
    if 'ni_parent' not in fin: fin['ni_parent'] = np.nan
    fin['ni_use'] = fin['ni_parent'].fillna(fin['ni'])
    fin['accr'] = (fin['ni'] - fin['cfo']) / fin['assets']
    P = pd.DataFrame({n: naver_daily(c)['close'] for c, n in UNIV.items()}).sort_index()
    M = P.resample('ME').last(); r1 = M.pct_change()

    rows = []
    for _, f in fin.iterrows():
        form_y = int(f['year']) + 1
        try:
            px = M.loc[f'{form_y}-06', f['name']].iloc[-1]
        except Exception:
            continue
        if not (pd.notna(px) and f.get('shares') and f.get('equity') and f['equity'] > 0):
            continue
        mc = px * f['shares']
        rows.append(dict(name=f['name'], form=form_y, ep=f['ni_use']/mc, bp=f['equity']/mc,
                         roe=f['ni_use']/f['equity'], accr=f['accr']))
    fp = pd.DataFrame(rows)

    def yearly_ret(names, y):
        per = r1.loc[f'{y}-07':f'{y+1}-06', [n for n in names if n in r1.columns]]
        return (1 + per.mean(axis=1)).prod() - 1 if not per.empty else None

    def run(col, asc=False, top=5, label='', filt=None):
        rets = {}
        for y in sorted(fp['form'].unique()):
            g = fp[fp['form'] == y].dropna(subset=[col])
            if filt is not None: g = filt(g)
            if len(g) < 8: continue
            ret = yearly_ret(g.sort_values(col, ascending=asc).head(top)['name'], y)
            if ret is not None: rets[y] = ret
        s = pd.Series(rets)
        if s.empty: return print(label, '데이터 없음')
        c = (1 + s).prod() ** (1 / len(s)) - 1
        print(f"{label:28s} 연평균 {c:6.1%} | 최악 {s.min():+.1%}")

    run('ep', top=99, label='벤치마크(동일가중)')
    run('ep', label='밸류 E/P 상위5')
    run('bp', label='밸류 B/P 상위5')
    run('roe', label='퀄리티 ROE 상위5')
    run('accr', asc=True, label='저발생액 상위5')
    run('ep', label='밸류∩저발생액',
        filt=lambda g: g[g['accr'] <= g['accr'].quantile(0.5)] if g['accr'].notna().sum() > 5 else g)


if __name__ == '__main__':
    main()
