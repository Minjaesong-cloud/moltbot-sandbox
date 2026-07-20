"""
자산군 전략 백테스트 (재현 스크립트).
데이터: FRED CSV (무료, API 키 불필요). 인터넷 접근 환경에서 실행.
전략: 매수보유 / 200일선 추세 / 12개월 모멘텀 / 60·40 / 리스크패리티 / 분산 추세추종(CTA).
주의: 자산군 레벨(개별종목 아님). 거래비용 미반영. rf=0. 인샘플. 과최적화 경계.
"""
import io, urllib.request, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
def fred(series):
    raw = urllib.request.urlopen(FRED+series, timeout=30).read().decode()
    d = pd.read_csv(io.StringIO(raw), na_values='.')
    d.columns = ['date','v']; d['date']=pd.to_datetime(d['date'])
    return d.set_index('date')['v'].dropna()

def build():
    eq=fred('NASDAQCOM'); y10=fred('DGS10'); oil=fred('DCOILWTICO'); oil=oil[oil>0]
    df=pd.concat([eq.rename('eq'),y10.rename('y10'),oil.rename('oil')],axis=1).sort_index()
    for c in ['eq','y10','oil']: df[c]=df[c].ffill()
    df=df.dropna(subset=['eq','y10'])
    D=7.0; dy=df['y10'].diff()/100
    df['bond_ret']=(df['y10'].shift(1)/100/252)-D*dy
    df['bond']=(1+df['bond_ret'].fillna(0)).cumprod()
    df['eq_ret']=df['eq'].pct_change().clip(-.5,.5)
    df['oil_ret']=df['oil'].pct_change().clip(-.5,.5)
    return df

def stats(ret,name):
    ret=ret.dropna()
    if len(ret)<50: return None
    yrs=len(ret)/252; cum=(1+ret).cumprod()
    return dict(name=name,CAGR=round((cum.iloc[-1]**(1/yrs)-1)*100,1),
        Vol=round(ret.std()*np.sqrt(252)*100,1),
        Sharpe=round((ret.mean()*252)/(ret.std()*np.sqrt(252)),2),
        MaxDD=round((cum/cum.cummax()-1).min()*100,1))

def tsmom(r,lvl,lb=252):
    sig=((lvl/lvl.shift(lb)-1)>0).reindex(r.index).shift(1).fillna(False); return r*sig.astype(float)
def ma(r,lvl,w=200):
    sig=(lvl>lvl.rolling(w).mean()).shift(1).fillna(False); return r*sig.astype(float)

if __name__=='__main__':
    df=build(); rows=[]
    rows+=[stats(df['eq_ret'],'Equity B&H'),stats(df['bond_ret'],'Bond B&H'),stats(df['oil_ret'],'Oil B&H')]
    rows+=[stats(ma(df['eq_ret'],df['eq']),'Equity 200d Trend'),stats(tsmom(df['eq_ret'],df['eq']),'Equity 12m Mom')]
    rows+=[stats(0.6*df['eq_ret']+0.4*df['bond_ret'],'60/40')]
    rets=df[['eq_ret','bond_ret','oil_ret']]; iv=1/rets.rolling(60).std(); w=iv.div(iv.sum(1),axis=0).shift(1)
    rows+=[stats((w*rets).sum(1).replace(0,np.nan).dropna(),'Risk Parity')]
    dt=(tsmom(df['eq_ret'],df['eq'])+tsmom(df['bond_ret'],df['bond'])+tsmom(df['oil_ret'],df['oil']))/3
    rows+=[stats(dt,'Diversified Trend (CTA)')]
    print(pd.DataFrame([r for r in rows if r]).to_string(index=False))
