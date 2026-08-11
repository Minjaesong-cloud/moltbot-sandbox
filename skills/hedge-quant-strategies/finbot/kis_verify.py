"""
KIS 모의투자 검증 스크립트 — **사용자 로컬 PC에서 실행** (클라우드 샌드박스는 KIS 포트 차단).

이 저장소를 클론한 뒤 로컬에서:
  1. skills/hedge-quant-strategies/data/.api_keys.json 생성 (git 제외됨):
     {"kis_appkey": "...", "kis_appsecret": "...", "kis_account": "50197748-01", "kis_mode": "paper"}
  2. python3 skills/hedge-quant-strategies/finbot/kis_verify.py
  3. 전 단계 통과 시 마지막에 모의 주문 1주 전송 여부를 물어본다 (y 입력 시에만).

검증 순서: 토큰 발급 → 삼성전자 현재가 → 계좌 잔고 → 주문 dry_run → (선택) 모의 매수 1주.
"""
import sys, json
from kis import token, price, balance, order

def step(name, fn):
    try:
        r = fn()
        print(f"✅ {name}: {str(r)[:200]}")
        return r
    except Exception as e:
        print(f"❌ {name} 실패: {str(e)[:300]}")
        print("   → 포트 차단 환경(클라우드 샌드박스 등)이면 로컬 PC에서 실행할 것.")
        sys.exit(1)

if __name__ == '__main__':
    step('1/5 토큰 발급', lambda: token()[:20] + '...')
    step('2/5 삼성전자 현재가', lambda: price('005930'))
    b = step('3/5 계좌 잔고', lambda: balance())
    out2 = b.get('output2') or [{}]
    print(f"   예수금 등 요약: {json.dumps(out2[0], ensure_ascii=False)[:200]}")
    step('4/5 주문 dry_run (전송 안 함)', lambda: order('005930', 1, 'buy', dry_run=True))
    ans = input("5/5 모의투자 계좌에 삼성전자 1주 시장가 매수를 실제 전송할까요? [y/N] ")
    if ans.strip().lower() == 'y':
        r = order('005930', 1, 'buy', dry_run=False)
        print("주문 응답:", json.dumps(r, ensure_ascii=False)[:300])
        print("→ KIS 앱/HTS 모의투자 화면에서 체결 확인.")
    else:
        print("주문 생략. 4단계까지 통과했으면 연동 검증 완료.")
