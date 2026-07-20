"""
Damodaran(NYU Stern) 공개 데이터셋 로더 + 산업 상대가치 스크리너.

소스: https://pages.stern.nyu.edu/~adamodar/pc/datasets/ (연 1~2회 갱신, 무료 공개)
- 산업별(미국 ~93개 산업): PER(pedata), PBV·ROE(pbvdata), 마진(margin), WACC(wacc), 베타(betas)
- 국가별: 국가 리스크 프리미엄·ERP(ctryprem — 한국 포함 150+개국)
- 시장: S&P500 장기 수익률(histretSP)

사용처 (experts/aswath-damodaran.md 의 프라이싱 규율을 데이터로):
- 상대가치(멀티플)는 "산업 평균 대비 어디에 있고, 그 차이가 펀더멘털(ROE·마진·성장·리스크)로
  설명되는가"를 물어야 한다. 이 모듈은 그 대조표(산업 스크리너)를 만든다.
- 국가 ERP는 해외(한국 포함) 기업 밸류에이션의 할인율 입력값.

주의: 미국 상장기업 기준 산업 평균이다. 한국 기업에 쓸 때는 국가 ERP를 더하고
회계·지배구조 차이를 감안할 것. 멀티플 차이 자체는 결론이 아니라 질문이다.
"""
import io, os, urllib.request
import pandas as pd

BASE = "https://pages.stern.nyu.edu/~adamodar/pc/datasets/"
DATASETS = {          # key -> 파일명
    'pe':      'pedata.xls',      # 산업별 PER (Current/Trailing/Forward, 적자기업 비율)
    'pbv':     'pbvdata.xls',     # 산업별 PBV·ROE
    'margin':  'margin.xls',      # 산업별 마진 (Gross/Operating/Net)
    'wacc':    'wacc.xls',        # 산업별 자본비용 (Beta, Cost of Equity/Debt/Capital)
    'beta':    'betas.xls',       # 산업별 베타 (레버드/언레버드)
    'ctryprem':'ctryprem.xls',    # 국가별 리스크 프리미엄·ERP
    'histret': 'histretSP.xls',   # S&P500·채권 장기 수익률(1928~)
}
_CACHE = os.environ.get('DAMODARAN_CACHE', os.path.expanduser('~/.cache/damodaran'))
UA = {'User-Agent': 'Mozilla/5.0 (research)'}


def _path(key):
    """다운로드(캐시). 파일은 수백 KB 수준."""
    os.makedirs(_CACHE, exist_ok=True)
    p = os.path.join(_CACHE, DATASETS[key])
    if not os.path.exists(p):
        req = urllib.request.Request(BASE + DATASETS[key], headers=UA)
        with open(p, 'wb') as f:
            f.write(urllib.request.urlopen(req, timeout=60).read())
    return p


def _find_header(df, key, scan=40, min_cells=3):
    """머리말(설명 행)이 긴 시트에서 실제 헤더 행 탐색: key 포함 + 비결측 셀 min_cells개 이상."""
    for i in range(min(scan, len(df))):
        row = df.iloc[i]
        if row.notna().sum() >= min_cells and any(key.lower() in str(v).lower() for v in row.dropna()):
            return i
    return None


def load_industry(key, sheet='Industry Averages'):
    """산업 데이터셋 하나를 DataFrame으로. 인덱스=Industry (~93개)."""
    raw = pd.read_excel(_path(key), sheet_name=sheet, header=None)
    h = _find_header(raw, 'Industry')
    if h is None:
        raise ValueError(f"{key}: 'Industry' 헤더 행을 찾지 못함 (시트 구조 변경 가능성)")
    df = raw.iloc[h + 1:].copy()
    df.columns = [str(c).strip() for c in raw.iloc[h]]
    icol = df.columns[0]
    df = df.dropna(subset=[icol]).set_index(icol)
    df.index.name = 'Industry'
    # 'Total Market' 같은 합계 행은 남겨둔다(시장 전체 벤치마크로 유용)
    # 숫자 변환은 사용처(_pick + to_numeric(errors='coerce'))에서 컬럼 단위로 수행
    return df


def _pick(df, *keywords):
    """키워드 전부를 포함하는 첫 컬럼명 (Damodaran 컬럼명이 해마다 조금씩 바뀌는 것 대응)."""
    for c in df.columns:
        if all(k.lower() in str(c).lower() for k in keywords):
            return c
    return None


def industry_screener():
    """PER·PBV·ROE·마진·자본비용·베타를 산업별로 병합한 상대가치 대조표."""
    pe, pbv, mg, wc = (load_industry(k) for k in ('pe', 'pbv', 'margin', 'wacc'))
    out = pd.DataFrame(index=pe.index)
    def add(df, col, name):
        if col: out[name] = pd.to_numeric(df[col], errors='coerce')
    add(pe,  _pick(pe, 'number', 'firm'),      '기업수')
    add(pe,  _pick(pe, 'current', 'pe'),       'PER(현재)')
    add(pe,  _pick(pe, 'forward', 'pe'),       'PER(포워드)')
    add(pe,  _pick(pe, 'money losing'),        '적자기업비율')
    add(pbv, _pick(pbv, 'pbv'),                'PBV')
    add(pbv, _pick(pbv, 'roe'),                'ROE')
    add(mg,  _pick(mg, 'gross'),               '매출총이익률')
    add(mg,  _pick(mg, 'net', 'margin'),       '순이익률')
    add(wc,  _pick(wc, 'beta'),                '베타')
    add(wc,  _pick(wc, 'cost of equity'),      '자기자본비용')
    add(wc,  _pick(wc, 'cost of capital'),     'WACC')
    # 핵심 대조: PBV가 ROE로 설명되는가 (PBV ≈ (ROE-g)/(CoE-g) 직관의 1차 근사)
    out['PBV/ROE'] = out['PBV'] / out['ROE'].where(out['ROE'] > 0)
    return out


def country_erp():
    """국가별 ERP 표. 컬럼: 지역, 무디스등급, 디폴트스프레드, 총ERP, 국가리스크프리미엄."""
    raw = pd.read_excel(_path('ctryprem'), sheet_name='ERPs by country', header=None)
    h = _find_header(raw, 'Country', scan=15)   # 헤더('Country', 'Moody's rating', ...)
    df = raw.iloc[h + 1:].copy()
    df.columns = [str(c).strip() for c in raw.iloc[h]]
    df = df.rename(columns={df.columns[0]: 'Country', df.columns[1]: 'Region'})
    df = df.dropna(subset=['Country']).set_index('Country')
    for c in df.columns[2:]:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df


def erp(country='Korea'):
    """국가 하나의 ERP 요약 dict. 부분 일치(예: 'Korea')."""
    t = country_erp()
    m = t[t.index.str.contains(country, case=False, na=False)]
    if m.empty:
        raise KeyError(f"{country}: ERP 표에 없음 (등급/CDS 없는 국가는 PRS 시트 참조)")
    r = m.iloc[0]
    tot = _pick(m, 'total equity risk'); crp = _pick(m, 'country risk'); ds = _pick(m, 'default spread')
    return {'국가': m.index[0], '지역': r.get('Region'),
            '총ERP': float(r[tot]) if tot else None,
            '국가리스크프리미엄': float(r[crp]) if crp else None,
            '디폴트스프레드': float(r[ds]) if ds else None}


if __name__ == '__main__':
    kr = erp('Korea')
    print(f"한국 ERP: 총 {kr['총ERP']:.2%} (국가 프리미엄 {kr['국가리스크프리미엄']:.2%}, "
          f"디폴트 스프레드 {kr['디폴트스프레드']:.2%})")
    s = industry_screener()
    print(f"\n산업 스크리너: {len(s)}개 산업")
    cols = ['PER(현재)', 'PBV', 'ROE', '순이익률', 'WACC']
    print("\n[PBV 상위 5 — 프리미엄이 ROE로 설명되는가?]")
    print(s.nlargest(5, 'PBV')[cols].to_string())
    print("\n[PBV 하위 5 — 싼 게 아니라 아픈 것 아닌가?]")
    print(s[s['기업수'] >= 10].nsmallest(5, 'PBV')[cols].to_string())
