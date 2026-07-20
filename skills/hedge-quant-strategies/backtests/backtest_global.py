"""
글로벌 멀티에셋 멀티전략 백테스트 (재현). 데이터: FRED CSV(무료).
자산: 미국(NASDAQ)·일본(니케이) 주식, 미 국채10/30, WTI·브렌트·천연가스, 원/엔/유로.
전략: 매수보유 / 12M 추세추종 / 리스크패리티 / 변동성타깃 추세 / 교차자산모멘텀 / 듀얼모멘텀 / 60·40.
주의: 자산군 레벨. 거래비용 미반영. rf=0. 인샘플. 과최적화 경계(파라미터 표준값 사용).
"""
import io, urllib.request, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
FRED="https://fred.stlouisfed.org/graph/fredgraph.csv?id="
def fred(s):
    raw=urllib.request.urlopen(FRED+s,timeout=30).read().decode()
    d=pd.read_csv(io.StringIO(raw),na_values='.'); d.columns=['date','v']
    d['date']=pd.to_datetime(d['date']); return d.set_index('date')['v'].dropna()
def build():
    us=fred('NASDAQCOM'); jp=fred('NIKKEI225'); oil=fred('DCOILWTICO'); oil=oil[oil>0]
    brent=fred('DCOILBRENTEU'); gas=fred('DHHNGSP'); y10=fred('DGS10'); y30=fred('DGS30')
    krw=fred('DEXKOUS'); jpy=fred('DEXJPUS'); eur=fred('DEXUSEU')
    p=pd.concat([us.rename('us'),jp.rename('jp'),oil.rename('oil'),brent.rename('brent'),
        gas.rename('gas'),y10.rename('y10'),y30.rename('y30'),krw.rename('krw'),
        jpy.rename('jpy'),eur.rename('eur')],axis=1).sort_index().ffill()
    R=pd.DataFrame(index=p.index)
    for tag,y,D in [('Bond10','y10',7.0),('Bond30','y30',17.0)]:
        R[tag]=(p[y].shift(1)/100/252)-D*(p[y].diff()/100)
    for nm,c in [('US_eq','us'),('JP_eq','jp'),('Oil','oil'),('Brent','brent'),('Gas','gas')]:
        R[nm]=p[c].pct_change().clip(-.4,.4)
    R['KRW']=(-p['krw'].pct_change()).clip(-.2,.2); R['JPY']=(-p['jpy'].pct_change()).clip(-.2,.2)
    R['EUR']=p['eur'].pct_change().clip(-.2,.2)
    return R
def stats(ret,name):
    ret=ret.dropna()
    if len(ret)<250: return
    yrs=len(ret)/252; cum=(1+ret).cumprod()
    print(f"{name:<34} CAGR {(cum.iloc[-1]**(1/yrs)-1)*100:>5.1f}%  Vol {ret.std()*np.sqrt(252)*100:>4.1f}%  "
          f"Sharpe {(ret.mean()*252)/(ret.std()*np.sqrt(252)):>4.2f}  MaxDD {(cum/cum.cummax()-1).min()*100:>6.1f}%")
def tsmom(R,a,lb=252):
    lvl=(1+R[a].fillna(0)).cumprod(); return R[a]*((lvl/lvl.shift(lb)-1)>0).shift(1).fillna(False)
def voltarget(ret,tgt=.10,win=40):
    rv=ret.rolling(win).std()*np.sqrt(252); return (ret*(tgt/rv).clip(upper=3).shift(1)).dropna()
if __name__=='__main__':
    R=build()
    for a in R.columns: stats(R[a],a+' 매수보유'); 
    print('---')
    sub=R[['US_eq','JP_eq','Bond10','Oil','Gas']]; iv=1/sub.rolling(60).std(); w=iv.div(iv.sum(1),axis=0).shift(1)
    stats((w*sub).sum(1).replace(0,np.nan),'리스크패리티')
    dt=pd.concat([tsmom(R,a) for a in ['US_eq','JP_eq','Bond10','Oil','Gas','EUR','JPY']],axis=1).mean(1)
    stats(dt,'글로벌 분산 추세추종(CTA)'); stats(voltarget(dt),'  +변동성타깃 10%')
    stats(0.6*R['US_eq']+0.4*R['Bond10'],'60/40')
