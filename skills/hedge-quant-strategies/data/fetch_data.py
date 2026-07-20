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



# ---------- 8. SEC Frames (한 요청으로 전 기업 단면 재무 — 팩터 구축용 ★) ----------
def sec_frame(tag, period, taxonomy='us-gaap', unit='USD'):
    """예: sec_frame('NetIncomeLoss','CY2023') → {cik: value} 전 기업.
    instant 항목은 CY2023Q4I, dei 주식수는 sec_frame('EntityCommonStockSharesOutstanding','CY2024Q2I','dei','shares')"""
    j=json.loads(_get(f"https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/{unit}/{period}.json"))
    return {d['cik']:d['val'] for d in j.get('data',[])}

# ---------- 9. Ken French 팩터 라이브러리 (1926~, 팩터의 정전) ----------
def ken_french(dataset='F-F_Research_Data_Factors'):
    """dataset: F-F_Research_Data_Factors(3팩터) | F-F_Momentum_Factor | F-F_Research_Data_5_Factors_2x3"""
    import zipfile, re
    raw=_get(f"https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/{dataset}_CSV.zip")
    z=zipfile.ZipFile(io.BytesIO(raw)); txt=z.read(z.namelist()[0]).decode('latin-1').splitlines()
    start=next(i for i,l in enumerate(txt) if ',' in l and ('Mkt-RF' in l or 'Mom' in l))
    rows=[l for l in txt[start+1:] if re.match(r'^\s*\d{6},',l)]
    df=pd.read_csv(io.StringIO(txt[start]+'\n'+'\n'.join(rows)))
    df.columns=['ym']+[c.strip() for c in df.columns[1:]]
    df['date']=pd.to_datetime(df['ym'].astype(str),format='%Y%m')
    return df.set_index('date').drop(columns='ym').astype(float)/100.0

# ---------- 10. 심리·기타 검증 소스 ----------
def crypto_fear_greed():  # 2018~ 일별 크립토 공포탐욕지수
    j=json.loads(_get("https://api.alternative.me/fng/?limit=0&format=json"))
    return pd.Series({pd.to_datetime(int(d['timestamp']),unit='s'):int(d['value']) for d in j['data']}).sort_index()
def blockchain_btc(chart='market-price', timespan='5years'):
    j=json.loads(_get(f"https://api.blockchain.info/charts/{chart}?timespan={timespan}&format=json"))
    return pd.Series({pd.to_datetime(v['x'],unit='s'):v['y'] for v in j['values']})
def gdelt_news_volume(query, timespan='3m'):
    """전세계 뉴스 볼륨 타임라인. ⚠ 5초당 1요청, 초과 시 장시간 429."""
    import urllib.parse
    j=json.loads(_get(f"https://api.gdeltproject.org/api/v2/doc/doc?query={urllib.parse.quote(query)}&mode=timelinevol&format=json&timespan={timespan}"))
    return pd.Series({pd.to_datetime(d['date']):d['value'] for d in j['timeline'][0]['data']})
def bis_eer(country='KR', last=1000):  # BIS 실질실효환율(일별)
    raw=_get(f"https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/D.N.B.{country}?format=csv&lastNObservations={last}").decode()
    d=pd.read_csv(io.StringIO(raw)); return d.set_index(pd.to_datetime(d['TIME_PERIOD']))['OBS_VALUE']
# ---------- 10.5 한국 시장 (Naver 금융 — ★2026-07 신규 검증, 최고의 무료 한국 소스) ----------
def naver_daily(symbol='KOSPI', start='19900101', end='20991231'):
    """한국 일별 시세. symbol: KOSPI(1990~)|KOSDAQ(1996~)|종목코드 6자리(예: '005930' 삼성전자).
    반환: DataFrame[open,high,low,close,volume,foreign] — foreign=외국인소진율(%, 지수는 0).
    KRX 정보데이터시스템은 차단 확인 — 이 엔드포인트가 유일하게 뚫린 한국 일별 소스."""
    import re
    url=(f"https://api.finance.naver.com/siseJson.naver?symbol={symbol}&requestType=1"
         f"&startTime={start}&endTime={end}&timeframe=day")
    raw=_get(url, headers={'User-Agent':'Mozilla/5.0'}).decode()
    rows=re.findall(r'\["(\d{8})",\s*([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*(\d+),\s*([\d.]+)',raw)
    d=pd.DataFrame(rows,columns=['date','open','high','low','close','volume','foreign'])
    d['date']=pd.to_datetime(d['date']); d=d.set_index('date').astype(float)
    return d.sort_index()

# ---------- 11. 변동성·스트레스·재정 (★2026-07 신규 검증) ----------
def cboe_index(index='VIX'):
    """CBOE 지수 일별 히스토리(1990~). index: VIX(OHLC — FRED VIXCLS는 종가만) | SKEW(테일리스크)"""
    raw=_get(f"https://cdn.cboe.com/api/global/us_indices/daily_prices/{index}_History.csv").decode()
    d=pd.read_csv(io.StringIO(raw)); d['DATE']=pd.to_datetime(d['DATE'])
    return d.set_index('DATE').sort_index()
def cboe_quote(symbol='AAPL'):
    """CBOE 지연 시세(개별 미국 주식·ETF, 키 불필요). current_price·bid·ask·OHLC."""
    return json.loads(_get(f"https://cdn.cboe.com/api/global/delayed_quotes/quotes/{symbol}.json"))['data']
def ofr_fsi():
    """OFR 금융스트레스지수 일별(2000~). 0=평균. 서브컴포넌트: Credit/Equity valuation/
    Safe assets/Funding/Volatility + 지역(US/선진/이머징). 리스크 레짐 게이트용."""
    raw=_get("https://www.financialresearch.gov/financial-stress-index/data/fsi.csv").decode()
    d=pd.read_csv(io.StringIO(raw)); d['Date']=pd.to_datetime(d['Date'])
    return d.set_index('Date').sort_index()
def nyfed_rates():
    """NY Fed 기준금리 스냅샷(SOFR·EFFR 등 + 30/90/180일 평균)."""
    return json.loads(_get("https://markets.newyorkfed.org/api/rates/all/latest.json"))['refRates']
def treasury_fiscal(endpoint='v2/accounting/od/debt_to_penny', params='page%5Bsize%5D=100&sort=-record_date'):
    """미 재무부 FiscalData(국가부채·경매·현금잔고 등). ⚠ page[size]는 URL 인코딩 필수."""
    j=json.loads(_get(f"https://api.fiscaldata.treasury.gov/services/api/fiscal_service/{endpoint}?{params}"))
    return pd.DataFrame(j['data'])

def nasdaq_symbols():
    raw=_get("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt").decode()
    return pd.read_csv(io.StringIO(raw),sep='|')[:-1]


# ---------- 12. 키 기반 API (★2026-07 사용자 키 확보 — .api_keys.json, git 제외) ----------
def _api_key(name):
    import os
    k = os.environ.get(name.upper() + '_API_KEY')
    if k: return k.strip()
    p = os.path.join(os.path.dirname(__file__), '.api_keys.json')
    if os.path.exists(p):
        return json.load(open(p)).get(name)
    raise RuntimeError(f"{name} 키 없음: 환경변수 {name.upper()}_API_KEY 또는 data/.api_keys.json")

def ecos(stat='722Y001', cycle='M', start='200001', end='209912', item='0101000', n=1000):
    """한국은행 ECOS. 예: 기준금리('722Y001',M,item 0101000), 국고채3y('817Y002',D,'010200000'),
    원달러('731Y001',D,'0000001'), M2('101Y004',M,'BBHA00'). 통계코드는 ecos.bok.or.kr 참조."""
    url=(f"https://ecos.bok.or.kr/api/StatisticSearch/{_api_key('ecos')}/json/kr/1/{n}/"
         f"{stat}/{cycle}/{start}/{end}/{item}")
    rows=json.loads(_get(url))['StatisticSearch']['row']
    s=pd.Series({r['TIME']: float(r['DATA_VALUE']) for r in rows if r['DATA_VALUE']})
    fmt={'M':'%Y%m','D':'%Y%m%d','A':'%Y','Q':None}[cycle]
    if fmt: s.index=pd.to_datetime(s.index,format=fmt)
    return s.sort_index()

def tiingo_daily(ticker='AAPL', start='1995-01-01', freq='daily'):
    """Tiingo 미국 주식/ETF 수정주가(30년+). 무료: 시간당 50건·월 500심볼 — 유니버스 남용 금지.
    freq: daily|weekly|monthly. 반환: DataFrame[adjClose, adjVolume...]"""
    url=(f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate={start}"
         f"&resampleFreq={freq}&format=json&token={_api_key('tiingo')}")
    d=pd.DataFrame(json.loads(_get(url)))
    d['date']=pd.to_datetime(d['date']).dt.tz_localize(None)
    return d.set_index('date')

def finnhub(path='quote', **params):
    """Finnhub (분당 60건). 예: finnhub('quote',symbol='AAPL'), finnhub('stock/metric',symbol='AAPL',metric='all'),
    finnhub('company-news',symbol='AAPL',**{'from':'2026-07-01','to':'2026-07-20'})"""
    import urllib.parse
    q=urllib.parse.urlencode({**params,'token':_api_key('finnhub')})
    return json.loads(_get(f"https://finnhub.io/api/v1/{path}?{q}"))

def eia(series='PET.WCESTUS1.W', n=100):
    """EIA 에너지(원유재고 등). ⚠ 2026-07 키 403 — 이메일 활성화 필요할 수 있음. 활성화 후 재시도."""
    j=json.loads(_get(f"https://api.eia.gov/v2/seriesid/{series}?api_key={_api_key('eia')}&length={n}"))
    d=j['response']['data']
    return pd.Series({x['period']: x['value'] for x in d}).sort_index()


if __name__=='__main__':
    print("[SEC] Apple 매출·순이익 최근:")
    m=sec_ticker_map(); cik=m['AAPL']
    rev=sec_concept(cik,'Revenues'); ni=sec_concept(cik,'NetIncomeLoss')
    print("  CIK",cik,"| 매출 rows",len(rev),"| 순이익 rows",len(ni),"| 최근순이익", ni.dropna().iloc[-1]['val'] if len(ni) else None)
    print("[CFTC] COT 최근 시장 수:", cftc_cot(200)['market_and_exchange_names'].nunique())
    print("[Crypto] BTC 최근가:", round(coingecko_market_chart('bitcoin',7).iloc[-1]))
    print("[IMF] 한국 실질GDP성장 2022:", imf('NGDP_RPCH','KOR').get('2022'))