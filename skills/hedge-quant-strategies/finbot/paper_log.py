"""
페이퍼 트래킹 — 엔진의 목표 포트폴리오를 실행 시점마다 기록해 실전 검증을 축적한다.

백테스트는 과거, 페이퍼 로그는 미래다: 기록이 쌓이면 "엔진이 실시간으로 냈던 판단"의
성과를 사후 조작 불가능하게 평가할 수 있다(Carver: 시스템을 믿으려면 라이브 기록이 필요).

사용: python paper_log.py  → paper_log.jsonl에 한 줄 추가 (같은 날 중복 실행은 덮어씀).
"""
import json, os, sys
import numpy as np
from strategy_engine import target_portfolio, valuation_context

LOG = os.path.join(os.path.dirname(__file__), 'paper_log.jsonl')

def record():
    today, port, cotz = target_portfolio()
    v = valuation_context()
    entry = {
        'date': str(today.date()),
        'weights': {r['자산']: r['목표비중'] for _, r in port.iterrows()},
        'trend': {r['자산']: r['추세'] for _, r in port.iterrows()},
        'gross': round(float(port['목표비중'].sum()), 3),
        'cot_z': round(float(cotz), 2) if np.isfinite(cotz) else None,
        'fsi': round(float(port.attrs.get('fsi', float('nan'))), 2)
               if np.isfinite(port.attrs.get('fsi', float('nan'))) else None,
        'implied_erp': v.get('내재ERP'),
    }
    lines = []
    if os.path.exists(LOG):
        lines = [l for l in open(LOG).read().splitlines()
                 if l.strip() and json.loads(l)['date'] != entry['date']]
    lines.append(json.dumps(entry, ensure_ascii=False))
    with open(LOG, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return entry

if __name__ == '__main__':
    e = record()
    print(json.dumps(e, ensure_ascii=False, indent=1))
    print(f"→ {LOG} ({sum(1 for _ in open(LOG))}개 기록)")
