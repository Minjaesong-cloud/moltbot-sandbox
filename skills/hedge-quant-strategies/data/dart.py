"""
DART(금융감독원 전자공시) API — 한국 기업 재무제표·주식수·공시.

키 필요(무료): https://opendart.fss.or.kr 발급 → 환경변수 DART_API_KEY 또는
이 파일 옆 .dart_key 파일(한 줄, git 제외됨)에 저장. **키를 코드/저장소에 넣지 말 것.**

핵심 API (하루 20,000건 한도):
- corp_codes(): 종목코드 ↔ DART 고유번호 매핑 (zip 다운로드, 캐시)
- annual_financials(corp_code, year): 연결(없으면 별도) 재무 — 자산·자본·순이익(지배/전체)·영업CF
  ※ 지배주주 귀속 순이익을 직접 제공 — 미국 frames의 NCI 태깅 함정(158개사)이 여기선 없음
- total_shares(corp_code): 보통주 발행주식총수
사용례: 한국 밸류·퀄리티·발생액 팩터 (backtests/KOREA-FUNDAMENTALS.md, finbot/kr_stock_engine.py)

주의: 연간보고서(reprt_code=11011)는 3월 말까지 제출 → 팩터 형성은 6월(look-ahead 회피).
가격과 결합 시 Naver 수정주가 × 현재 주식수 = 시총 근사(분할 무관, 증자·자사주만 오차).
"""
import io, json, os, re, time, zipfile, urllib.request
import pandas as pd

_CACHE = os.environ.get('DART_CACHE', os.path.expanduser('~/.cache/dart'))


def _key():
    k = os.environ.get('DART_API_KEY')
    if k: return k.strip()
    p = os.path.join(os.path.dirname(__file__), '.dart_key')
    if os.path.exists(p): return open(p).read().strip()
    raise RuntimeError("DART 키 없음: 환경변수 DART_API_KEY 또는 data/.dart_key 파일에 저장")


def _get(url, timeout=120, tries=3):
    for t in range(tries):
        try:
            return urllib.request.urlopen(url, timeout=timeout).read()
        except Exception:
            if t == tries - 1: raise
            time.sleep(5 * (t + 1))


def corp_codes():
    """종목코드(6자리) → (corp_code, 회사명). 상장사만. 첫 호출 시 ~4MB 다운로드(캐시)."""
    os.makedirs(_CACHE, exist_ok=True)
    p = os.path.join(_CACHE, 'corpcode.zip')
    if not os.path.exists(p):
        data = _get(f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={_key()}", timeout=400)
        open(p, 'wb').write(data)
    xml = zipfile.ZipFile(p).read('CORPCODE.xml').decode()
    out = {}
    # ⚠ 반드시 <list> 레코드 단위로 파싱 — 레코드 경계를 넘는 정규식은 엉뚱한 회사를 매핑한다
    for rec in re.finditer(r'<list>(.*?)</list>', xml, re.S):
        r = rec.group(1)
        sc = re.search(r'<stock_code>(\d{6})</stock_code>', r)
        if not sc: continue
        cc = re.search(r'<corp_code>(\d+)</corp_code>', r).group(1)
        nm = re.search(r'<corp_name>([^<]*)</corp_name>', r).group(1)
        md = re.search(r'<modify_date>(\d+)</modify_date>', r)
        prev = out.get(sc.group(1))
        if prev is None or (md and md.group(1) > prev[2]):   # 중복 종목코드 → 최신 법인
            out[sc.group(1)] = (cc, nm, md.group(1) if md else '0')
    return {k: (v[0], v[1]) for k, v in out.items()}


def annual_financials(corp_code, year):
    """연간 연결재무(없으면 별도). dict: assets, equity, ni(전체), ni_parent(지배), cfo, fs."""
    for fs in ('CFS', 'OFS'):
        j = json.loads(_get(f"https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
                            f"?crtfc_key={_key()}&corp_code={corp_code}&bsns_year={year}"
                            f"&reprt_code=11011&fs_div={fs}"))
        if j['status'] != '000': continue
        out = {'fs': fs}
        for it in j['list']:
            nm = it['account_nm'].replace(' ', '')
            amt = str(it.get('thstrm_amount', '')).replace(',', '')
            if not amt or not amt.lstrip('-').isdigit(): continue
            v, sj = int(amt), it.get('sj_div')
            if sj == 'BS' and nm == '자산총계': out['assets'] = v
            elif sj == 'BS' and nm == '자본총계': out['equity'] = v
            elif sj in ('IS', 'CIS') and '지배기업' in nm and '순이익' in nm and '비지배' not in nm:
                out.setdefault('ni_parent', v)
            elif sj in ('IS', 'CIS') and nm in ('당기순이익', '당기순이익(손실)'):
                out.setdefault('ni', v)
            elif sj == 'CF' and nm == '영업활동현금흐름': out['cfo'] = v
        return out if 'assets' in out else None
    return None


def total_shares(corp_code, year=2024):
    """보통주 발행주식총수 (사업보고서 기준)."""
    j = json.loads(_get(f"https://opendart.fss.or.kr/api/stockTotqySttus.json"
                        f"?crtfc_key={_key()}&corp_code={corp_code}&bsns_year={year}&reprt_code=11011"))
    if j['status'] != '000': return None
    for it in j['list']:
        if '보통주' in str(it.get('se', '')):
            n = str(it.get('istc_totqy', '')).replace(',', '')
            if n.isdigit(): return int(n)
    return None


if __name__ == '__main__':
    codes = corp_codes()
    cc, name = codes['005930']
    f = annual_financials(cc, 2023)
    s = total_shares(cc)
    print(name, f"자산 {f['assets']/1e12:.0f}조 자본 {f['equity']/1e12:.0f}조 "
          f"지배NI {f['ni_parent']/1e12:.1f}조 CFO {f['cfo']/1e12:.1f}조 주식수 {s/1e6:.0f}M")
