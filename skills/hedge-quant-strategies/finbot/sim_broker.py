"""
가상 증권계좌 (모의 브로커) — KIS 연결 전까지 실제 가격으로 매매 시뮬레이션.

실제와 같게: Naver 실시간 종가로 체결, 수수료 0.015%, 매도 시 거래세 0.15%,
정수 주식 수량만. 상태는 sim_account.json에 저장(커밋됨 — 기록 자체가 검증 자료).

한계(정직하게): 종가 체결 가정(호가 스프레드·슬리피지 없음), 배당 미반영.
실전은 이것보다 조금 나쁘다고 보면 된다.
"""
import json, os
from datetime import date

FEE = 0.00015          # 수수료 0.015% (매수·매도)
SELL_TAX = 0.0015      # 증권거래세 0.15% (매도만, KOSPI 2025)
STATE = os.path.join(os.path.dirname(__file__), 'sim_account.json')


def load(initial_cash=10_000_000):
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {'cash': initial_cash, 'initial': initial_cash, 'positions': {},  # code -> {qty, name, avg_price}
            'trades': [], 'valuations': []}


def save(acct):
    json.dump(acct, open(STATE, 'w'), ensure_ascii=False, indent=1)


def buy(acct, code, name, qty, price, day=None, reason='', thesis=''):
    """매수. reason=매수 근거, thesis=무효화 조건("이게 깨지면 판다") — 감정 배제 장치:
    매도 판단은 이 조건이 깨졌는지만 본다."""
    cost = qty * price * (1 + FEE)
    if qty <= 0 or cost > acct['cash'] + 1: return False
    acct['cash'] -= cost
    p = acct['positions'].get(code, {'qty': 0, 'name': name, 'avg_price': 0.0})
    p['avg_price'] = (p['avg_price'] * p['qty'] + price * qty) / (p['qty'] + qty)
    p['qty'] += qty; p['name'] = name
    acct['positions'][code] = p
    if thesis:
        acct.setdefault('theses', {})[code] = {'종목': name, '매수일': day or str(date.today()),
                                               '매수근거': reason, '무효화조건': thesis}
    acct['trades'].append({'date': day or str(date.today()), 'side': 'buy', 'code': code,
                           'name': name, 'qty': qty, 'price': price, 'cost': round(cost),
                           'reason': reason})
    return True


def sell(acct, code, qty, price, day=None, reason=''):
    """매도. reason에 어떤 무효화 조건이 깨졌는지 기록 — 근거 없는 매도를 구조적으로 막는다."""
    p = acct['positions'].get(code)
    if not p or qty <= 0 or qty > p['qty']: return False
    proceeds = qty * price * (1 - FEE - SELL_TAX)
    acct['cash'] += proceeds
    pnl = (price - p['avg_price']) * qty
    p['qty'] -= qty
    if p['qty'] == 0:
        del acct['positions'][code]
        acct.get('theses', {}).pop(code, None)
    acct['trades'].append({'date': day or str(date.today()), 'side': 'sell', 'code': code,
                           'name': p['name'], 'qty': qty, 'price': price,
                           'proceeds': round(proceeds), 'realized_pnl': round(pnl),
                           'reason': reason})
    return True


def valuate(acct, prices, day=None, benchmarks=None):
    """prices: {code: 현재가}. benchmarks: {'sp500':..., 'kospi':...} 동시 기록 —
    목표가 'S&P 초과수익 + 저변동'이므로 매 평가마다 벤치마크를 같이 남겨 비교 가능하게."""
    pos_val = sum(p['qty'] * prices.get(c, p['avg_price']) for c, p in acct['positions'].items())
    total = acct['cash'] + pos_val
    entry = {'date': day or str(date.today()), 'total': round(total),
             'cash': round(acct['cash']), 'positions_value': round(pos_val),
             'return_pct': round((total / acct['initial'] - 1) * 100, 2),
             **(benchmarks or {})}
    acct['valuations'] = [v for v in acct['valuations'] if v['date'] != entry['date']] + [entry]
    return entry


def vs_benchmark(acct):
    """운용 시작 이후 전략 vs S&P500 vs KOSPI 비교 (벤치마크 기록이 2개 이상일 때)."""
    vs = [v for v in acct['valuations'] if v.get('sp500')]
    if len(vs) < 2: return None
    f, l = vs[0], vs[-1]
    strat = l['total'] / vs[0]['total'] - 1 if vs[0]['total'] else 0
    return {'기간': f"{f['date']}~{l['date']}",
            '전략': f"{(l['total']/f['total']-1)*100:+.2f}%",
            'S&P500': f"{(l['sp500']/f['sp500']-1)*100:+.2f}%",
            'KOSPI': f"{(l['kospi']/f['kospi']-1)*100:+.2f}%" if f.get('kospi') else None,
            '초과수익(vs S&P)': f"{((l['total']/f['total'])-(l['sp500']/f['sp500']))*100:+.2f}%p"}
