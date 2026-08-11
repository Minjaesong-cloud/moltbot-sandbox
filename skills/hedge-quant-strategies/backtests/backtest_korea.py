import pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
F='fred/'
def L(id,c):
    d=pd.read_csv(F+id+'.csv',na_values='.'); d.columns=['date',c]
    d['date']=pd.to_datetime(d['date']); return d.set_index('date')[c].dropna()
kr=L('SPASTT01KRM661N','kr'); us=L('NASDAQCOM','us'); krw=L('DEXKOUS','krw')
def M(s): return s.resample("ME").last()
kr=M(kr); usm=M(us); krwm=M(krw)
df=pd.concat([kr,usm,krwm],axis=1).dropna(subset=['kr'])
df['kr_ret']=df['kr'].pct_change(); df['us_ret']=df['us'].pct_change()
df['usd_krw_ret']=df['krw'].pct_change()
df['us_in_krw']=(1+df['us_ret'])*(1+df['usd_krw_ret'])-1
def stats(ret,name):
    ret=ret.dropna()
    if len(ret)<24: return
    yrs=len(ret)/12; cum=(1+ret).cumprod()
    print(f"{name:<32} CAGR {(cum.iloc[-1]**(1/yrs)-1)*100:>5.1f}%  Vol {ret.std()*np.sqrt(12)*100:>4.1f}%  Sharpe {(ret.mean()*12)/(ret.std()*np.sqrt(12)):>4.2f}  MaxDD {(cum/cum.cummax()-1).min()*100:>6.1f}%  ({ret.index[0].year}~)")
def mom(rc,lc,lb=12):
    lvl=df[lc]; sig=((lvl/lvl.shift(lb)-1)>0).shift(1).fillna(False); return df[rc]*sig
def ma(rc,lc,w=10):
    lvl=df[lc]; sig=(lvl>lvl.rolling(w).mean()).shift(1).fillna(False); return df[rc]*sig
print("=== 한국(KOSPI계열 월간 1981~) 전략 ===")
stats(df['kr_ret'],'KOSPI 매수보유')
stats(mom('kr_ret','kr'),'KOSPI 12개월 모멘텀')
stats(ma('kr_ret','kr'),'KOSPI 10개월 이평추세')
kra=df['kr']/df['kr'].shift(12)-1
usl=(1+df['us_in_krw']).cumprod(); uska=usl/usl.shift(12)-1
pk=((kra>=uska)&(kra>0)).shift(1).fillna(False); pu=((uska>kra)&(uska>0)).shift(1).fillna(False)
dm=df['kr_ret']*pk+df['us_in_krw']*pu
stats(dm,'한미 듀얼모멘텀(현금방어)')
stats(df['us_in_krw'],'미국주식(원화환산) 매수보유')
stats(0.5*df['kr_ret']+0.5*df['us_in_krw'],'한미 반반(원화)')
print("\n=== 한국 위기 연간수익률(%) ===")
def yr(r,y):
    x=r[r.index.year==y].dropna(); return round(((1+x).prod()-1)*100,1) if len(x)>=6 else None
S={'KOSPI 매수보유':df['kr_ret'],'KOSPI 추세추종':mom('kr_ret','kr'),'한미 듀얼모멘텀':dm,'미국(원화)':df['us_in_krw']}
ys=[1997,1998,2000,2008,2011,2018,2020,2022]
print(f"{'전략':<16}"+''.join(f"{y:>7}" for y in ys))
for n,r in S.items(): print(f"{n:<16}"+''.join(f"{str(yr(r,y)):>7}" for y in ys))
