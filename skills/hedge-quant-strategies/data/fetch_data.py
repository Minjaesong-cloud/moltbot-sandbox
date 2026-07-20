"""
무료·공개 금융 데이터 하베스터 (finbot용). 키 불필요 소스 위주.
확인된 작동 소스: FRED, SEC EDGAR(미국 재무·공시), CFTC COT(포지셔닝), CoinGecko/Coinbase(암호화폐),
IMF/World Bank(글로벌 매크로), ECB(환율), GitHub 공개 데이터셋(주가 패널).
주의: 각 소스의 이용약관·rate limit 준수. SEC는 User-Agent 헤더 필수. GDELT는 5초당 1요청.
"""
import io, json, time, urllib.request, pandas as pd
UA={'User-Agent':'finbot research contact@example.com'}
def _get(url, headers=None, timeout=40):
    req=urllib.request.Request(url, headers=headers or UA)
    return urllib.request.urlopen(req, timeout=timeout).read()

# ---------- 1. FRED (매크로·시장: 금리·FX·원자재·지수·신용스프레드·경제지표) ----------
def fred(series):  # 예: fred('DGS10'), fred('SP500'), fred('DEXKOUS')
    raw=_get("https://fred.stlouisfed.org/graph/fredgraph.csv?id="+series).decode()
    d=pd.read_csv(io.StringIO(raw), na_values='.'); d.columns=['date','value']
    d['date']=pd.to_datetime(d['date']); return d.set_index('date')['value'].dropna()

# ---------- 2. SEC EDGAR (미국 기업 펀더멘털·공시) ----------
def sec_ticker_map():  # ticker -> CIK
    j=json.loads(_get("https://www.sec.gov/files/company_tickers.json"))
    return {v['ticker']:str(v['cik_str']).zfill(10) for v in j.values()}
def sec_concept(cik, tag, taxonomy='us-gaap'):  # 특정 재무항목 시계열 (예: Revenues, NetIncomeLoss)
    url=f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{tag}.json"
    j=json.loads(_get(url)); rows=[]
    for unit,vals in j.get('units',{}).items():
        for v in vals: rows.append({'end':v.get('end'),'val':v.get('val'),'form':v.get('form'),'fy':v.get('fy'),'fp':v.get('fp')})
    return pd.DataFrame(rows)
def sec_companyfacts(cik):  # 전체 재무 팩트 (모든 XBRL 항목)
    return json.loads(_get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"))
def sec_filings(cik):  # 공시 목록 (10-K, 8-K, 13F 등)
    return json.loads(_get(f"https://data.sec.gov/submissions/CIK{cik}.json"))

# ---------- 3. CFTC COT (투기·상업 포지셔닝 — 매크로·추세 신호) ----------
def cftc_cot(limit=5000):  # Legacy Futures-only COT (Socrata)
    url=f"https://publicreporting.cftc.gov/resource/6dca-aqww.json?$limit={limit}&$order=report_date_as_yyyy_mm_dd DESC"
    return pd.DataFrame(json.loads(_get(url.replace(' ','%20'))))

# ---------- 4. 암호화폐 (CoinGecko 시총·시계열, Coinbase OHLCV) ----------
def coingecko_market_chart(coin='bitcoin', days=365, vs='usd'):
    j=json.loads(_get(f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency={vs}&days={days}"))
    p=pd.DataFrame(j['prices'],columns=['ts','price']); p['date']=pd.to_datetime(p['ts'],unit='ms')
    return p.set_index('date')['price']
def coinbase_candles(product='BTC-USD', granularity=86400):  # daily OHLCV
    j=json.loads(_get(f"https://api.exchange.coinbase.com/products/{product}/candles?granularity={granularity}"))
    d=pd.DataFrame(j,columns=['ts','low','high','open','close','volume']); d['date']=pd.to_datetime(d['ts'],unit='s')
    return d.set_index('date').sort_index()

# ---------- 5. 글로벌 매크로 (IMF, World Bank) ----------
def imf(indicator, country):  # 예: imf('NGDP_RPCH','KOR') 실질GDP성장
    j=json.loads(_get(f"https://www.imf.org/external/datamapper/api/v1/{indicator}/{country}"))
    return pd.Series(j['values'][indicator][country])
def worldbank(country, indicator):  # 예: worldbank('KR','NY.GDP.MKTP.CD')
    j=json.loads(_get(f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&per_page=500"))
    return pd.DataFrame([{'year':r['date'],'value':r['value']} for r in j[1]]).dropna()

# ---------- 6. ECB 환율(유로 기준 전 통화 장기) ----------
def ecb_fx():
    raw=_get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.csv").decode()
    d=pd.read_csv(io.StringIO(raw)); d['Date']=pd.to_datetime(d['Date']); return d.set_index('Date').sort_index()

# ---------- 7. GitHub 공개 주가 패널 (S&P500 2013-2018 개별종목) ----------
def github_sp500():
    raw=_get("https://raw.githubusercontent.com/plotly/datasets/master/all_stocks_5yr.csv").decode()
    d=pd.read_csv(io.StringIO(raw),parse_dates=['date'])
    return d.pivot_table(index='date',columns='Name',values='close').sort_index()

if __name__=='__main__':
    print("[SEC] Apple 매출·순이익 최근:")
    m=sec_ticker_map(); cik=m['AAPL']
    rev=sec_concept(cik,'Revenues'); ni=sec_concept(cik,'NetIncomeLoss')
    print("  CIK",cik,"| 매출 rows",len(rev),"| 순이익 rows",len(ni),"| 최근순이익", ni.dropna().iloc[-1]['val'] if len(ni) else None)
    print("[CFTC] COT 최근 시장 수:", cftc_cot(200)['market_and_exchange_names'].nunique())
    print("[Crypto] BTC 최근가:", round(coingecko_market_chart('bitcoin',7).iloc[-1]))
    print("[IMF] 한국 실질GDP성장 2022:", imf('NGDP_RPCH','KOR').get('2022'))
