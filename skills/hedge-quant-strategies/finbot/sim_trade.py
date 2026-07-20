"""
모의 매매 실행기 — 한국 듀얼 모멘텀 전략을 가상 계좌(1천만원)로 실제 운용.

동작: kr_stock_engine의 이번 달 픽(모멘텀 상위5 + KOSPI 게이트 + 발생액 필터)에 맞춰
가상 계좌를 리밸런스한다. 게이트 OFF면 전량 매도(현금). 이미 보유 중인 픽은 유지.
매 실행마다 평가액을 기록 — 이 기록이 전략의 실시간 성적표다.

사용: python sim_trade.py            → 리밸런스 + 평가
     python sim_trade.py --value    → 평가만 (매매 없이)
주기: 리밸런스는 월 1회(백테스트 전제와 동일 — 잦은 실행은 회전비용만 늘림),
     평가는 주간 루틴이 수행.
"""
import sys, json
from datetime import date
import sim_broker as B
from kr_stock_engine import picks, vol_scale


def current_prices(codes):
    from fetch_data import naver_daily
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
    out = {}
    for c in codes:
        try:
            out[c] = float(naver_daily(c, start='20260601')['close'].iloc[-1])
        except Exception:
            pass
    return out


def rebalance():
    gate, kospi, df, sel = picks()
    acct = B.load()
    target_codes = list(sel['코드']) if gate else []
    names = dict(zip(df['코드'], df['종목']))
    all_codes = set(target_codes) | set(acct['positions'])
    px = current_prices(all_codes)
    today = str(date.today())

    # 1) 픽에서 빠진 보유 종목 전량 매도
    for code in list(acct['positions']):
        if code not in target_codes and code in px:
            B.sell(acct, code, acct['positions'][code]['qty'], px[code], today)
    # 2) 신규 픽 매수 — 가용 현금을 빈 슬롯에 균등 배분
    new = [c for c in target_codes if c not in acct['positions'] and c in px]
    if new:
        per = acct['cash'] / len(new) * 0.995   # 수수료 여유
        for code in new:
            qty = int(per // px[code])
            if qty > 0:
                B.buy(acct, code, names.get(code, code), qty, px[code], today)
    v = B.valuate(acct, px, today)
    B.save(acct)
    return gate, kospi, sel, v, acct


def value_only():
    acct = B.load()
    px = current_prices(set(acct['positions']))
    v = B.valuate(acct, px)
    B.save(acct)
    return v, acct


if __name__ == '__main__':
    if '--value' in sys.argv:
        v, acct = value_only()
        print(f"평가액 {v['total']:,}원 ({v['return_pct']:+.2f}%) | 현금 {v['cash']:,}원")
        for c, p in acct['positions'].items():
            print(f"  {p['name']}: {p['qty']}주 @ 평단 {p['avg_price']:,.0f}")
    else:
        gate, kospi, sel, v, acct = rebalance()
        print(f"KOSPI {kospi:,.0f} | 게이트 {'ON' if gate else 'OFF → 전량 현금'}"
              f" | 권장 스케일 ×{vol_scale()} (참고)")
        print(f"평가액 {v['total']:,}원 ({v['return_pct']:+.2f}%) | 현금 {v['cash']:,}원")
        print("보유:")
        for c, p in acct['positions'].items():
            print(f"  {p['name']}: {p['qty']}주 @ 평단 {p['avg_price']:,.0f}")
        print(f"누적 거래 {len(acct['trades'])}건 — 기록: sim_account.json")
