"""
finbot 개별 종목 스크리너 — SEC XBRL frames(실제 재무) 팩터 + Damodaran 산업 맥락.

백테스트 근거 (backtests/FUNDAMENTAL-FACTORS.md, SEC 실데이터 검증):
  밸류(E/P) 상위    : 18.2% vs 시장 13.0% (연환산, 2013-18 패널)
  퀄리티(ROE) 상위  : MaxDD -6.6% (방어적)
  저발생액          : 15.6% vs 고발생액 12.8% (Sloan anomaly)
→ 세 팩터를 결합: 발생액 최악 20% 제외 후 밸류+퀄리티 순위 합산.

데이터의 정직한 한계:
  - EntityPublicFloat = 유통주식 시가(내부자 지분 제외) ≠ 전체 시총. 내부자 지분 큰 기업의
    E/P가 과대평가된다. 또한 측정 시점이 회계연도 중간(Q2 말)이라 가격이 최대 1년 낡았다.
  - frames는 회계연도 말이 제각각인 기업을 CY 기준으로 섞는다.
  - 따라서 이것은 **트레이딩 신호가 아니라 후보 발굴 스크린**이다. 통과 종목은
    financial-statement-analysis 스킬(숫자의 질)과 Damodaran 산업 대조(damodaran.py)로 심사.

사용: python stock_screener.py  → 상위 후보 + 산업 컨텍스트 출력.
"""
import sys, os, json, urllib.request
import pandas as pd, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from fetch_data import sec_frame, sec_ticker_map, sec_filings, cboe_quote

MIN_FLOAT   = 2e8    # 유통시총 $200M 미만(마이크로캡) 제외 — 유동성·데이터 품질
ACCRUAL_CUT = 0.80   # 발생액 상위(=최악) 20% 제외
TOP_N       = 20


def build_panel(cy='CY2025'):
    """SEC frames → CIK 단면 패널. 한 요청당 전 상장사.

    NCI(비지배지분) 조정: 표준 XBRL에선 NetIncomeLoss = 지배주주 귀속이지만, CY2025 실측에서
    187/1,216개 기업이 NI에 NCI를 포함해 태깅(THC 사례 — PIPELINE-DEMO.md). NI≈ProfitLoss인데
    NCI가 따로 있으면 NI − NCI로 보정한다."""
    q4i = cy + 'Q4I'
    ni     = pd.Series(sec_frame('NetIncomeLoss', cy))
    pl     = pd.Series(sec_frame('ProfitLoss', cy))
    nci    = pd.Series(sec_frame('NetIncomeLossAttributableToNoncontrollingInterest', cy))
    cfo    = sec_frame('NetCashProvidedByUsedInOperatingActivities', cy)
    eq     = sec_frame('StockholdersEquity', q4i)
    assets = sec_frame('Assets', q4i)
    flt    = sec_frame('EntityPublicFloat', cy + 'Q2I', 'dei', 'USD')
    bad = ni.index.intersection(pl.index).intersection(nci.index)
    bad = bad[(ni[bad] - pl[bad]).abs() < nci[bad].abs() * 0.1]   # NI≈PL(NCI 포함 태깅) 기업만
    ni[bad] = ni[bad] - nci[bad]
    df = pd.DataFrame({'ni': ni, 'cfo': cfo, 'equity': eq, 'assets': assets, 'float': flt}).dropna()
    df.attrs['nci_adjusted'] = len(bad)
    return df


def score(df):
    df = df[(df['float'] > MIN_FLOAT) & (df['equity'] > 0) & (df['assets'] > 0)].copy()
    df['ep']      = df['ni'] / df['float']                 # 밸류 (float 기준 — 한계는 모듈 주석)
    df['roe']     = df['ni'] / df['equity']                # 퀄리티
    df['accrual'] = (df['ni'] - df['cfo']) / df['assets']  # 이익의 질 (낮을수록 좋음)
    df = df[df['accrual'] <= df['accrual'].quantile(ACCRUAL_CUT)]   # Sloan 필터
    df['score'] = df['ep'].rank(pct=True) + df['roe'].rank(pct=True)
    return df.sort_values('score', ascending=False)


def annotate(df, top_n=TOP_N):
    """상위 후보에 티커·회사명·SIC 산업 + 진짜 시총 E/P(CBOE 실시간가 × SEC 주식수) 부여.
    float 기반 E/P의 왜곡(내부자 지분·가격 시차)을 후보 단계에서 교정한다."""
    tmap = {int(cik): t for t, cik in sec_ticker_map().items()}
    try:      # dei 주식수 (최신 분기 instant → 없으면 전 분기)
        shares = sec_frame('EntityCommonStockSharesOutstanding', 'CY2026Q1I', 'dei', 'shares')
    except Exception:
        shares = {}
    top = df.head(top_n * 2).copy()          # 티커 없는 CIK(펀드 등) 대비 여유
    top['ticker'] = [tmap.get(c) for c in top.index]
    top = top.dropna(subset=['ticker']).head(top_n)
    names, sics, mcap_ep = [], [], []
    for cik, row in top.iterrows():
        try:
            f = sec_filings(str(cik).zfill(10))
            names.append(f.get('name', '')[:32]); sics.append(f.get('sicDescription', '')[:36])
        except Exception:
            names.append(''); sics.append('')
        try:
            mc = cboe_quote(row['ticker'])['current_price'] * shares[cik]
            mcap_ep.append(row['ni'] / mc if mc > 0 else np.nan)
        except Exception:
            mcap_ep.append(np.nan)
    top['회사'], top['SIC산업'], top['ep_mcap'] = names, sics, mcap_ep
    return top


if __name__ == '__main__':
    panel = build_panel()
    print(f"패널: {len(panel)}개 기업 (frames 교집합, CY2025) | NCI 태깅 보정 {panel.attrs.get('nci_adjusted','?')}개")
    ranked = score(panel)
    print(f"필터 후: {len(ranked)}개 (float>${MIN_FLOAT/1e6:.0f}M, 자본>0, 발생액 최악 20% 제외)")
    top = annotate(ranked)
    out = top[['ticker', '회사', 'SIC산업', 'ep', 'ep_mcap', 'roe', 'accrual', 'float']].copy()
    out.columns = ['티커', '회사', 'SIC산업', 'E/P(float)', 'E/P(시총)', 'ROE', '발생액/자산', '유통시총']
    out['유통시총'] = (out['유통시총'] / 1e9).round(1).astype(str) + 'B'
    for c in ['E/P(float)', 'E/P(시총)', 'ROE', '발생액/자산']:
        out[c] = (out[c] * 100).round(1)
    print("\n[밸류+퀄리티 상위 (발생액 필터 통과), % 단위 — E/P(시총)=CBOE 실시간가×SEC 주식수 기준]")
    print(out.to_string(index=False))
    both = out.dropna(subset=['E/P(시총)'])
    if len(both):
        infl = (both['E/P(float)'] / both['E/P(시총)']).replace([np.inf,-np.inf],np.nan).dropna()
        print(f"\nfloat E/P가 시총 E/P 대비 과대한 후보(배율>1.5): "
              f"{', '.join(both.loc[infl[infl>1.5].index,'티커'])}")
    print("\n다음 단계: ① financial-statement-analysis 스킬로 숫자의 질 검증")
    print("          ② data/damodaran.py 산업 스크리너로 산업 평균 대비 설명 안 되는 격차인지 확인")
    print("주의: float 기반 E/P는 내부자 지분 큰 기업에서 과대. 스크린이지 신호가 아님.")
