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


def buy(acct, code, name, qty, price, day=None):
    cost = qty * price * (1 + FEE)
    if qty <= 0 or cost > acct['cash'] + 1: return False
    acct['cash'] -= cost
    p = acct['positions'].get(code, {'qty': 0, 'name': name, 'avg_price': 0.0})
    p['avg_price'] = (p['avg_price'] * p['qty'] + price * qty) / (p['qty'] + qty)
    p['qty'] += qty; p['name'] = name
    acct['positions'][code] = p
    acct['trades'].append({'date': day or str(date.today()), 'side': 'buy', 'code': code,
                           'name': name, 'qty': qty, 'price': price, 'cost': round(cost)})
    return True


def sell(acct, code, qty, price, day=None):
    p = acct['positions'].get(code)
    if not p or qty <= 0 or qty > p['qty']: return False
    proceeds = qty * price * (1 - FEE - SELL_TAX)
    acct['cash'] += proceeds
    pnl = (price - p['avg_price']) * qty
    p['qty'] -= qty
    if p['qty'] == 0: del acct['positions'][code]
    acct['trades'].append({'date': day or str(date.today()), 'side': 'sell', 'code': code,
                           'name': p['name'], 'qty': qty, 'price': price,
                           'proceeds': round(proceeds), 'realized_pnl': round(pnl)})
    return True


def valuate(acct, prices, day=None):
    """prices: {code: 현재가}. 평가액 기록 후 요약 반환."""
    pos_val = sum(p['qty'] * prices.get(c, p['avg_price']) for c, p in acct['positions'].items())
    total = acct['cash'] + pos_val
    entry = {'date': day or str(date.today()), 'total': round(total),
             'cash': round(acct['cash']), 'positions_value': round(pos_val),
             'return_pct': round((total / acct['initial'] - 1) * 100, 2)}
    acct['valuations'] = [v for v in acct['valuations'] if v['date'] != entry['date']] + [entry]
    return entry
