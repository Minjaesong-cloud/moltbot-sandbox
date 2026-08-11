"""
라이브 브리핑 — 신뢰 소스에서 현재 정세·시황·AI 동향을 실시간 조회(저장 안 함).

원칙: 미리 저장한 요약을 최신인 척하지 않는다. 매 실행이 그 시점의 실시간 조회다.
소스는 references/sources.md의 검증된 allowlist만. 인기≠신뢰.

구현: 무료 접근 가능한 공식 소스(FRED·IMF·중앙은행 등) + RSS. 페이월 매체는 URL만 안내.
Firecrawl/WebSearch 도구가 있는 대화에서는 그쪽이 더 풍부 — 이 스크립트는 도구 없는
환경(루틴 등)의 폴백이자 정형 지표 조회용.

사용: python live_brief.py [geopolitics|macro|ai|all]
"""
import sys, os, json, urllib.request
from datetime import datetime, timezone

UA = {'User-Agent': 'Mozilla/5.0 (global-intelligence brief)'}


def _get(url, timeout=12):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read().decode('utf-8', 'replace')


def _fred_latest(series, label):
    """FRED 최신값 — 정형 매크로 지표(실시간, 무료)."""
    try:
        import csv, io
        raw = _get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}")
        rows = [r for r in csv.reader(io.StringIO(raw))][1:]
        rows = [r for r in rows if r[1] not in ('.', '')]
        if rows:
            d, v = rows[-1]
            return f"  {label}: {v} ({d})"
    except Exception as e:
        return f"  {label}: 조회 실패({str(e)[:30]})"
    return f"  {label}: 데이터 없음"


def _rss_titles(url, n=5):
    """RSS 최신 헤드라인 — 속보성 소스(실시간)."""
    import re
    try:
        xml = _get(url)
        items = re.findall(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', xml, re.S)
        return [t.strip() for t in items[1:n + 1] if t.strip()]
    except Exception:
        return []


def macro():
    print("=== 글로벌 매크로 (실시간, 무료 정형 지표) ===")
    print(_fred_latest('DGS10', '미 10년 국채금리'))
    print(_fred_latest('DGS2', '미 2년 국채금리'))
    print(_fred_latest('T10Y2Y', '장단기 스프레드(10Y-2Y)'))
    print(_fred_latest('DEXKOUS', '원/달러 환율'))
    print(_fred_latest('DTWEXBGS', '달러 인덱스(광의)'))
    print(_fred_latest('DCOILWTICO', 'WTI 유가'))
    print(_fred_latest('VIXCLS', 'VIX'))
    print(_fred_latest('BAMLH0A0HYM2', '하이일드 스프레드'))
    print("→ 심층 시황·중앙은행 코멘트는 references/sources.md의 IMF·BIS·Fed·FT를 라이브 조회.")


def geopolitics():
    print("=== 국제정세 (실시간 헤드라인) ===")
    feeds = [
        ('Reuters World', 'https://feeds.reuters.com/reuters/worldNews'),
        ('UN News', 'https://news.un.org/feed/subscribe/en/news/all/rss.xml'),
    ]
    got = False
    for name, url in feeds:
        titles = _rss_titles(url)
        if titles:
            got = True
            print(f"[{name}]")
            for t in titles:
                print(f"  · {t}")
    if not got:
        print("  RSS 조회 실패 — 대화 중이면 Firecrawl/WebSearch로 sources.md의 CFR·CSIS·")
        print("  Foreign Affairs·GZERO를 라이브 조회할 것.")


def ai():
    print("=== AI 최신 동향 (실시간) ===")
    feeds = [
        ('Anthropic News', 'https://www.anthropic.com/rss.xml'),
        ('Google DeepMind', 'https://deepmind.google/blog/rss.xml'),
    ]
    got = False
    for name, url in feeds:
        titles = _rss_titles(url)
        if titles:
            got = True
            print(f"[{name}]")
            for t in titles:
                print(f"  · {t}")
    if not got:
        print("  RSS 조회 실패 — 공식 블로그(anthropic.com/news, openai.com/blog,")
        print("  deepmind.google/blog)를 라이브 조회하거나 ai-engineering 스킬의 소스 참조.")


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    print(f"[조회 시각(UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}] "
          "— 저장 아님, 이 시점의 실시간 조회\n")
    if which in ('macro', 'all'): macro(); print()
    if which in ('geopolitics', 'all'): geopolitics(); print()
    if which in ('ai', 'all'): ai(); print()
    print("\n⚠ 이 결과는 조회 시점 기준. '지금'을 물으면 항상 재조회할 것(저장본 재사용 금지).")
