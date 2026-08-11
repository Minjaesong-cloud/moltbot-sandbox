"""
finbot 한국 종목 엔진 — 듀얼 모멘텀 (검증: backtests/KOREA-DAILY.md §4)

전략: 24개 대형주에서 12-1 모멘텀 상위 5 + KOSPI 10개월 이평 게이트(절대추세).
검증치(2000~2026, 월간): CAGR 18.3% / Sharpe 0.72 / MaxDD -33.1%
비용 민감도: 회전율 월 21%(한쪽), 0.3%/편도 반영 시 CAGR 16.6% — 비용 생존 확인.

정직한 한계:
- 유니버스가 오늘의 대형주 24개 = 생존편향. 절대 수익 기대치는 백테스트보다 낮춰 잡을 것
  (Carver: 기대 샤프의 절반로 사이징). 배당 미포함, 월 1회 리밸런스 전제.
- 외국인소진율은 정보로만 표시(횡단면 필터 검증 실패 — 같은 문서 §4).

사용: python kr_stock_engine.py  → 이번 달 픽 + kr_paper_log.jsonl 기록.
"""
import json, os, time
import pandas as pd, numpy as np
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from fetch_data import naver_daily

UNIVERSE = {'005930':'삼성전자','000660':'SK하이닉스','005380':'현대차','000270':'기아',
'005490':'POSCO','051910':'LG화학','035420':'네이버','017670':'SKT','030200':'KT','015760':'한전',
'055550':'신한지주','034730':'SK','003550':'LG','000810':'삼성화재','009150':'삼성전기',
'010130':'고려아연','004020':'현대제철','066570':'LG전자','012330':'현대모비스','006400':'삼성SDI',
'068270':'셀트리온','035720':'카카오','032830':'삼성생명','086790':'하나금융'}
TOP_N = 5
LOG = os.path.join(os.path.dirname(__file__), 'kr_paper_log.jsonl')


def accrual_flags():
    """발생액 최악 20% 종목 표시(제외용). 검증: 듀얼모멘텀 MaxDD -33→-28%, 수익 손실 없음
    (KOREA-FUNDAMENTALS.md). DART 키 없거나 실패 시 빈 set(필터 생략)."""
    try:
        from dart import corp_codes, annual_financials
        from concurrent.futures import ThreadPoolExecutor
        cmap = corp_codes()
        import datetime
        fy = datetime.date.today().year - 1 if datetime.date.today().month >= 7 else datetime.date.today().year - 2
        def one(code):
            f = annual_financials(cmap[code][0], fy)
            if f and all(k in f for k in ('ni', 'cfo', 'assets')):
                return code, (f['ni'] - f['cfo']) / f['assets']
            return code, np.nan
        with ThreadPoolExecutor(6) as ex:
            accr = dict(ex.map(one, list(UNIVERSE)))
        s = pd.Series(accr).dropna()
        return set(s[s > s.quantile(0.8)].index) if len(s) >= 10 else set()
    except Exception:
        return set()


def picks():
    kospi = naver_daily('KOSPI')['close']
    km = kospi.resample('ME').last()
    gate = bool((km > km.rolling(10).mean()).iloc[-1])
    excl = accrual_flags()
    rows = []
    for code, name in UNIVERSE.items():
        try:
            d = naver_daily(code, start='20240101')
            c = d['close']
            mom = c.iloc[-22] / c.asof(c.index[-1] - pd.DateOffset(months=12)) - 1  # 12-1 (직전 1개월 제외)
            rows.append(dict(코드=code, 종목=name, 모멘텀=round(float(mom), 3),
                             외국인소진율=round(float(d['foreign'].iloc[-1]), 1),
                             발생액필터=('제외' if code in excl else ''),
                             기준일=str(c.index[-1].date())))
            time.sleep(0.2)
        except Exception:
            continue
    df = pd.DataFrame(rows).sort_values('모멘텀', ascending=False).reset_index(drop=True)
    pool = df[df['발생액필터'] != '제외'] if len(df[df['발생액필터'] != '제외']) >= TOP_N else df
    sel = pool.head(TOP_N) if gate else df.head(0)
    return gate, float(kospi.iloc[-1]), df, sel


def vol_scale(target=0.12, cap=1.5):
    """모멘텀 크래시 방어(Barroso–Santa Clara): 타깃 12% / KOSPI 최근 6개월 실현변동성.
    검증(KOREA-DAILY.md §7): 샤프 0.72→0.75, MaxDD -33→-25%, 단 CAGR 18.3→12.7%
    (급등 연도를 깎는 비용). 강제가 아니라 권장 배율로만 표시한다."""
    k = naver_daily('KOSPI', start='20250101')['close']
    rv = float(k.pct_change().tail(126).std() * np.sqrt(252))
    return round(min(target / rv, cap), 2) if rv > 0 else 1.0


if __name__ == '__main__':
    gate, k, df, sel = picks()
    print(f"KOSPI {k:,.0f} | 10개월 추세 게이트: {'ON' if gate else 'OFF — 전량 현금'}")
    try:
        print(f"권장 포지션 스케일(변동성 12% 타깃): ×{vol_scale()} — 모멘텀 크래시 방어(선택)")
    except Exception:
        pass
    print("\n[모멘텀 12-1 순위 (전체)]")
    print(df.to_string(index=False))
    if gate:
        print(f"\n→ 이번 달 픽 (동일가중 {TOP_N}종목): {', '.join(sel['종목'])}")
    entry = {'date': str(pd.Timestamp.today().date()), 'kospi': round(k, 1), 'gate': gate,
             'picks': sel['종목'].tolist(), 'momentum': dict(zip(df['종목'], df['모멘텀']))}
    lines = []
    if os.path.exists(LOG):
        lines = [l for l in open(LOG).read().splitlines()
                 if l.strip() and json.loads(l)['date'] != entry['date']]
    lines.append(json.dumps(entry, ensure_ascii=False))
    open(LOG, 'w').write('\n'.join(lines) + '\n')
    print(f"\n기록 → {LOG}")
    print("주의: 생존편향 유니버스 — 기대치는 백테스트의 절반으로(Carver). 월 1회만 리밸런스.")
