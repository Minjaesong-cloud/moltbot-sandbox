"""
통합 후보 리포트 — 스크리너 상위 후보를 Damodaran 산업 평균과 자동 대조.

파이프라인의 ③단계(산업 맥락, PIPELINE-DEMO.md에선 수동)를 자동화한다:
후보의 SIC 산업명을 키워드로 Damodaran 산업 행에 매핑 → 시총 E/P vs 산업 E/P(1/PER),
ROE vs 산업 ROE를 나란히 — "격차가 펀더멘털로 설명되는가"를 묻는 표를 만든다.

사용: python candidate_report.py  → 표 출력 (스크리너 실행 포함, 수 분 소요).
"""
import os, sys
import pandas as pd, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from stock_screener import build_panel, score, annotate
from damodaran import industry_screener

# SIC 산업명 키워드 → Damodaran 산업명 (수동 매핑 — 자주 나오는 것부터; 없으면 미매핑 표시)
SIC2DAMO = [
    ('Oil & Gas', 'Oil/Gas (Production and Exploration)'),
    ('Petroleum', 'Oil/Gas (Production and Exploration)'),
    ('Drilling', 'Oilfield Svcs/Equip.'),
    ('Insurance Agents', 'Insurance (Brokers)'),
    ('Fire, Marine', 'Insurance (Prop/Cas.)'),
    ('Life Insurance', 'Insurance (Life)'),
    ('Pharmaceutical', 'Drugs (Pharmaceutical)'),
    ('Biological', 'Drugs (Biotechnology)'),
    ('Prepackaged Software', 'Software (System & Application)'),
    ('Metal Mining', 'Metals & Mining'),
    ('Real Estate Investment', 'R.E.I.T.'),
    ('Hotels', 'Hotel/Gaming'),
    ('Medical', 'Hospitals/Healthcare Facilities'),
    ('Retail-Department', 'Retail (General)'),
    ('Retail-Family Clothing', 'Retail (Special Lines)'),
    ('Retail-Catalog', 'Retail (Special Lines)'),
    ('Poultry', 'Food Processing'),
    ('Food', 'Food Processing'),
    ('State Commercial Banks', 'Banks (Regional)'),
    ('National Commercial Banks', 'Bank (Money Center)'),
    ('Business Credit', 'Financial Svcs. (Non-bank & Insurance)'),
    ('Semiconductors', 'Semiconductor'),
    ('Steel', 'Steel'),
    ('Air Transportation', 'Air Transport'),
]


def map_industry(sic):
    for kw, damo in SIC2DAMO:
        if kw.lower() in str(sic).lower():
            return damo
    return None


def report(top_n=15):
    damo = industry_screener()
    top = annotate(score(build_panel()), top_n)
    rows = []
    for _, r in top.iterrows():
        d = map_industry(r['SIC산업'])
        row = dict(티커=r['ticker'], SIC산업=str(r['SIC산업'])[:28],
                   EP시총=round(r['ep_mcap'] * 100, 1) if pd.notna(r['ep_mcap']) else None,
                   ROE=round(r['roe'] * 100, 1))
        if d is not None and d in damo.index:
            di = damo.loc[d]
            per = di.get('PER(현재)')
            row.update(산업=d[:26],
                       산업EP=round(100 / per, 1) if pd.notna(per) and per > 0 else None,
                       산업ROE=round(di.get('ROE') * 100, 1) if pd.notna(di.get('ROE')) else None)
        else:
            row.update(산업='(미매핑)', 산업EP=None, 산업ROE=None)
        rows.append(row)
    df = pd.DataFrame(rows)
    df['EP격차'] = df['EP시총'] - df['산업EP']    # 양수 = 산업보다 싸다 → "왜?"를 물을 것
    return df


if __name__ == '__main__':
    df = report()
    print(df.to_string(index=False))
    print("\n읽는 법: EP격차 > 0 = 산업 평균보다 싸다. 그 다음 질문은 '왜 싼가' —")
    print("  ROE가 산업보다 낮으면 정당한 할인, 높은데도 싸면 조사 가치(또는 데이터 함정).")
    print("  financial-statement-analysis 스킬로 숫자의 질 검증 후 판단할 것.")
