"""
한국투자증권 KIS Developers API 클라이언트 — finbot 실집행 다리.

⚠️ 상태: 모의투자 키·계좌 확보(2026-07-20). 단 **클라우드 샌드박스는 KIS 포트(9443/29443)가
egress 정책으로 차단**되어 여기서는 연결 불가 확인(portquiz 테스트) — **로컬 PC에서
kis_verify.py로 검증할 것**. 검증 전까지 실전 사용 금지.

키 설정 (data/.api_keys.json — git 제외):
  "kis_appkey": "...", "kis_appsecret": "...", "kis_account": "12345678-01",
  "kis_mode": "paper"   # paper(모의투자) | real(실전) — 반드시 paper로 검증 후 real

안전 원칙:
- 기본 모드는 paper. real 전환은 사람이 .api_keys.json을 직접 수정할 때만.
- 주문 함수는 dry_run=True가 기본 — 실제 전송하려면 dry_run=False 명시.
- 레이트리밋: 실전 REST 초당 20건 — 호출 사이 최소 간격 유지.
"""
import json, os, time, urllib.request

_BASE = {'real': 'https://openapi.koreainvestment.com:9443',
         'paper': 'https://openapivts.koreainvestment.com:29443'}
# 모의투자는 tr_id 앞글자가 V, 실전은 T
_TR = {'buy':  {'real': 'TTTC0802U', 'paper': 'VTTC0802U'},
       'sell': {'real': 'TTTC0801U', 'paper': 'VTTC0801U'},
       'balance': {'real': 'TTTC8434R', 'paper': 'VTTC8434R'}}
_TOKEN_CACHE = os.path.expanduser('~/.cache/kis_token.json')


def _keys():
    p = os.path.join(os.path.dirname(__file__), '..', 'data', '.api_keys.json')
    k = json.load(open(p))
    need = ['kis_appkey', 'kis_appsecret', 'kis_account']
    if any(n not in k for n in need):
        raise RuntimeError("KIS 키 없음: data/.api_keys.json에 kis_appkey/kis_appsecret/kis_account 추가")
    return k['kis_appkey'], k['kis_appsecret'], k['kis_account'], k.get('kis_mode', 'paper')


def _req(path, body=None, headers=None, method=None):
    ak, sk, acct, mode = _keys()
    url = _BASE[mode] + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method or ('POST' if data else 'GET'),
                                 headers={'Content-Type': 'application/json', **(headers or {})})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def token(force=False):
    """접근토큰 (24시간 유효 — 캐시. KIS는 잦은 재발급을 제한한다)."""
    if not force and os.path.exists(_TOKEN_CACHE):
        c = json.load(open(_TOKEN_CACHE))
        if time.time() < c.get('expires_at', 0) - 3600:
            return c['access_token']
    ak, sk, acct, mode = _keys()
    j = _req('/oauth2/tokenP', {'grant_type': 'client_credentials', 'appkey': ak, 'appsecret': sk})
    c = {'access_token': j['access_token'], 'expires_at': time.time() + int(j.get('expires_in', 86400))}
    os.makedirs(os.path.dirname(_TOKEN_CACHE), exist_ok=True)
    json.dump(c, open(_TOKEN_CACHE, 'w'))
    return c['access_token']


def _auth_headers(tr_id):
    ak, sk, acct, mode = _keys()
    return {'authorization': f'Bearer {token()}', 'appkey': ak, 'appsecret': sk, 'tr_id': tr_id}


def price(code='005930'):
    """현재가. 검증 전 — 실패 시 Naver naver_daily()로 대체 가능."""
    j = _req(f'/uapi/domestic-stock/v1/quotations/inquire-price'
             f'?fid_cond_mrkt_div_code=J&fid_input_iscd={code}',
             headers=_auth_headers('FHKST01010100'))
    o = j['output']
    return {'현재가': int(o['stck_prpr']), '전일대비율': float(o['prdy_ctrt']),
            '거래량': int(o['acml_vol'])}


def balance():
    """계좌 잔고·보유종목."""
    ak, sk, acct, mode = _keys()
    cano, prdt = acct.split('-')
    j = _req(f'/uapi/domestic-stock/v1/trading/inquire-balance'
             f'?CANO={cano}&ACNT_PRDT_CD={prdt}&AFHR_FLPR_YN=N&OFL_YN=&INQR_DVSN=02'
             f'&UNPR_DVSN=01&FUND_STTL_ICLD_YN=N&FNCG_AMT_AUTO_RDPT_YN=N&PRCS_DVSN=00'
             f'&CTX_AREA_FK100=&CTX_AREA_NK100=',
             headers=_auth_headers(_TR['balance'][mode]))
    return j


def order(code, qty, side='buy', price_krw=0, dry_run=True):
    """주문. price_krw=0이면 시장가. **dry_run=True 기본 — 실제 전송은 명시적으로만.**"""
    ak, sk, acct, mode = _keys()
    cano, prdt = acct.split('-')
    body = {'CANO': cano, 'ACNT_PRDT_CD': prdt, 'PDNO': code,
            'ORD_DVSN': '01' if price_krw == 0 else '00',
            'ORD_QTY': str(qty), 'ORD_UNPR': str(price_krw)}
    if dry_run:
        return {'dry_run': True, 'mode': mode, 'side': side, 'body': body,
                'note': '전송 안 함. 실제 주문은 order(..., dry_run=False)'}
    if mode == 'real':
        print('⚠️ 실전 주문 전송:', side, code, qty)
    return _req('/uapi/domestic-stock/v1/trading/order-cash', body,
                headers=_auth_headers(_TR[side][mode]))


if __name__ == '__main__':
    try:
        print(price('005930'))
        print(order('005930', 1, 'buy'))   # dry_run
    except RuntimeError as e:
        print(e)
