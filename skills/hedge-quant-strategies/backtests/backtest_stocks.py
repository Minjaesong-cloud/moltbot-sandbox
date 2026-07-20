"""
종목 레벨 팩터 백테스트 (재현). 데이터: GitHub plotly/datasets S&P500 5yr (2013-2018).
전략: 동일가중 벤치 / 모멘텀(12-1) 롱·롱숏 / 로우볼 / 단기 리버설 / 페어트레이딩.
주의: 단일 강세장 레짐, 거래비용 미반영, 생존편향, 펀더멘털 없음(밸류·퀄리티 불가).
"""
import urllib.request, io, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
URL="https://raw.githubusercontent.com/plotly/datasets/master/all_stocks_5yr.csv"
def load():
    raw=urllib.request.urlopen(URL,timeout=60).read().decode()
    d=pd.read_csv(io.StringIO(raw),parse_dates=['date'])
    px=d.pivot_table(index='date',columns='Name',values='close').sort_index()
    px=px.dropna(axis=1,thresh=int(px.shape[0]*0.95)).ffill().dropna(axis=1)
    return px
def stats(r,name):
    r=r.dropna()
    if len(r)<12: return
    yrs=len(r)/12; cum=(1+r).cumprod()
    print(f"{name:<30} CAGR {(cum.iloc[-1]**(1/yrs)-1)*100:>6.1f}%  Sharpe {(r.mean()*12)/(r.std()*np.sqrt(12)):>5.2f}  MaxDD {(cum/cum.cummax()-1).min()*100:>6.1f}%")
def quint(sig,ret,top=True,q=0.2):
    out=[]
    for dt in ret.index:
        if dt not in sig.index: out.append(np.nan); continue
        s=sig.loc[dt].dropna()
        if len(s)<50: out.append(np.nan); continue
        n=int(len(s)*q); pk=s.nlargest(n).index if top else s.nsmallest(n).index
        out.append(ret.loc[dt,pk].mean())
    return pd.Series(out,index=ret.index)
if __name__=='__main__':
    px=load(); ret=px.pct_change(); mret=px.resample('ME').last().pct_change(); mlvl=px.resample('ME').last()
    stats(mret.mean(axis=1),'동일가중 벤치마크')
    mom=mlvl.shift(1)/mlvl.shift(13)-1
    stats(quint(mom,mret,True),'모멘텀 상위20% 롱'); stats(quint(mom,mret,True)-quint(mom,mret,False),'모멘텀 롱숏')
    stats(quint(-ret.rolling(126).std().resample('ME').last(),mret,True),'로우볼 롱')
    stats(quint(-(mlvl.shift(1)/mlvl.shift(2)-1),mret,True),'단기 리버설')
