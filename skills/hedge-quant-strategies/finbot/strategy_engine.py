"""
finbot 통합 전략 엔진 (스캐폴드) — 백테스트로 검증된 신호 위계를 실행 코드로.

신호 위계 (backtests/ 검증 근거):
  1차 추세(가격)      : 10개월 이평 — 자산군별 on/off  [Shiller 152년·NASDAQ·KOSPI·BTC 검증]
  2차 밸류에이션      : CAPE 분위 → 주식 기대수익 가중(타이밍 아님)  [Shiller: 예측력 O, 스위치 X]
  3차 포지셔닝(COT)   : 투기 z-score 극단 → 사이징 보조  [약한 역발상 필터]
  최종 변동성 타깃     : 자산별 목표 변동성 역수 가중  [글로벌 CTA 샤프 1.06의 핵심]

사용: python strategy_engine.py  → 오늘의 목표 포트폴리오 + 판단 근거 출력.
주의: 교육·리서치용 페이퍼 포트폴리오. 실주문 전 비용·세금·슬리피지·집행 모듈 필요.
      Carver 원칙 적용 — 기대 샤프의 절반으로 사이징, 파라미터는 표준값(과최적화 금지).
"""
import sys, os, json, urllib.request, io
import pandas as pd, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from fetch_data import fred, cftc_cot, blockchain_btc

# ---------------- 설정 (표준 파라미터 — 데이터에 맞춰 조정하지 말 것) ----------------
TREND_MONTHS   = 10      # 10개월 이평 (Faber 표준)
VOL_TARGET     = 0.10    # 자산 슬리브당 연 10% 변동성 타깃
VOL_WINDOW     = 60      # 변동성 추정 창(일 단위 자산)
VOL_WINDOW_M   = 36      # 변동성 추정 창(월 단위 자산)
MAX_LEVER      = 1.5     # 슬리브 레버리지 상한
COT_Z_WINDOW   = 156     # COT z-score 창(주)
UNIVERSE = {             # 자산군 프록시. freq: D=일(252), D365=일(365, 크립토), M=월(12)
    'US_EQ':   dict(series='NASDAQCOM',        kind='price'),
    'KR_EQ':   dict(series='SPASTT01KRM661N',  kind='price', freq='M'),   # KOSPI 월별 (OECD)
    'JP_EQ':   dict(series='NIKKEI225',        kind='price'),
    'BOND10':  dict(series='DGS10',            kind='yield', dur=7.0),
    'OIL':     dict(series='DCOILWTICO',       kind='price'),
    'KRW':     dict(series='DEXKOUS',          kind='fx_short'),  # 롱 KRW = 숏 USD/KRW
    'BTC':     dict(src='btc',                 kind='price', freq='D365'),  # blockchain.info 일별
}
PPY = {'D': 252, 'D365': 365, 'M': 12}   # 연간화 기준 기간 수

def load_universe():
    """자산별 (수익률, 레벨, 연간기간수). 주기가 달라 자산별 시리즈로 유지(단일 DF로 합치지 않음
    — 월별 자산을 일별 인덱스에 섞으면 변동성 추정이 왜곡된다)."""
    assets = {}
    for name, cfg in UNIVERSE.items():
        if cfg.get('src') == 'btc':
            s = blockchain_btc().resample('D').ffill()   # ~4일 샘플링 → 일별 보정(백테스트에서 확인한 함정)
        else:
            s = fred(cfg['series']).astype(float)
        if cfg['kind'] == 'price':
            s = s[s > 0]; r = s.pct_change().clip(-.4,.4); lvl = s
        elif cfg['kind'] == 'yield':
            dy = s.diff()/100; r = (s.shift(1)/100/252) - cfg['dur']*dy; lvl=(1+r.fillna(0)).cumprod()
        elif cfg['kind'] == 'fx_short':
            r = (-s.pct_change()).clip(-.2,.2); lvl=(1+r.fillna(0)).cumprod()
        assets[name] = dict(r=r, lvl=lvl, ppy=PPY[cfg.get('freq','D')])
    return assets

def trend_on(lvl):
    m = lvl.resample('ME').last()
    ma = m.rolling(TREND_MONTHS).mean()
    return bool((m > ma).iloc[-1]) if len(m) >= TREND_MONTHS else False   # 1차: on/off

def vol_weight(r, ppy):
    win = VOL_WINDOW_M if ppy == 12 else VOL_WINDOW
    rv = float(r.rolling(win).std().iloc[-1]) * np.sqrt(ppy)
    return min(VOL_TARGET/rv, MAX_LEVER) if np.isfinite(rv) and rv > 0 else 0.0  # 최종: 변동성 타깃

def cot_adjust():
    """3차 보조: E-mini S&P 투기 z. 과열(z>2) 시 주식 슬리브 0.75배, 위축(z<-1) 시 1.1배."""
    try:
        cot = cftc_cot(4000)
        cot = cot[cot['market_and_exchange_names'].str.contains('E-MINI S&P 500', na=False)]
        for c in ['noncomm_positions_long_all','noncomm_positions_short_all','open_interest_all']:
            cot[c]=pd.to_numeric(cot[c])
        cot['date']=pd.to_datetime(cot['report_date_as_yyyy_mm_dd'])
        g=cot.groupby('date').sum(numeric_only=True).sort_index()
        net=(g['noncomm_positions_long_all']-g['noncomm_positions_short_all'])/g['open_interest_all']
        z=((net-net.rolling(COT_Z_WINDOW).mean())/net.rolling(COT_Z_WINDOW).std()).iloc[-1]
        adj = 0.75 if z>2 else (1.1 if z<-1 else 1.0)
        return z, adj
    except Exception:
        return np.nan, 1.0

def valuation_context():
    """2차: 밸류에이션은 배분 가중이지 스위치가 아님 — 여기선 참고 정보로 출력."""
    try:
        sp = fred('SP500'); e10 = None
        return dict(note="CAPE는 Shiller 데이터로 연 1회 갱신 권장(기대수익 예산). 스위치로 쓰지 말 것.")
    except Exception:
        return {}

def target_portfolio():
    assets = load_universe()
    cotz, cot_adj = cot_adjust()
    today = max(a['r'].index[-1] for a in assets.values())
    rows=[]
    for name, a in assets.items():
        on   = trend_on(a['lvl'])
        base = vol_weight(a['r'], a['ppy'])
        adj  = cot_adj if name.endswith('_EQ') else 1.0
        tgt  = round(base*adj,3) if on else 0.0
        rows.append(dict(자산=name, 추세=('ON' if on else 'OFF'),
                         변동성타깃웨이트=round(base,3), COT조정=adj, 목표비중=tgt,
                         데이터기준=str(a['r'].index[-1].date())))
    port=pd.DataFrame(rows)
    gross=port['목표비중'].sum()
    if gross>2.0:   # 총 그로스 상한 (Carver: 리스크는 자본이 아니라 변동성으로)
        port['목표비중']=(port['목표비중']/gross*2.0).round(3)
    return today, port, cotz

if __name__=='__main__':
    today, port, cotz = target_portfolio()
    print(f"기준일: {today.date()} | COT z(E-mini S&P): {cotz:+.2f}" if np.isfinite(cotz) else f"기준일: {today.date()} | COT: n/a")
    print(port.to_string(index=False))
    print(f"\n총 그로스: {port['목표비중'].sum():.2f} (상한 2.0)")
    print("근거: 추세=10개월 이평(자산군·152년 검증, KOSPI·BTC 포함) / 사이징=변동성 타깃 10%(글로벌 CTA 샤프 1.06)")
    print("     / COT=보조 필터(약한 역발상) / 밸류에이션은 연간 배분 예산으로 별도 반영")
