"""
스킬 자동 갱신 — 신뢰 전문가 채널의 새 콘텐츠만 감지·수집 큐 생성.

원칙: sources_registry.json의 allowlist만. '전부 뒤지기' 금지(인기≠신뢰).
파이프라인: RSS로 새 영상 감지(가벼움·확실) → 수집 큐 → yt-dlp 자막 수집(재시도 파도)
→ 서브에이전트 추출 → 대상 스킬 references 갱신 → 커밋. 이 스크립트는 감지+큐까지;
자막 수집·추출은 무거워서 루틴이 인내심 있게(429 재시도) 수행.

사용:
  python skill_refresh.py            # 새 콘텐츠 감지 → harvest_queue.json
  python skill_refresh.py --resolve  # channel_id 없는 소스의 handle 해결 시도
"""
import os, sys, json, re, time, urllib.request
from datetime import datetime

HERE = os.path.dirname(__file__)
REG = os.path.join(HERE, 'sources_registry.json')
STATE = os.path.join(HERE, 'refresh_state.json')
QUEUE = os.path.join(HERE, 'harvest_queue.json')
UA = {'User-Agent': 'Mozilla/5.0'}


def _get(url, timeout=25):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read().decode('utf-8', 'replace')


def resolve_channel_id(handle):
    """유튜브 핸들 → channel_id (채널 페이지 HTML의 channelId). 실패 시 None."""
    try:
        html = _get(f"https://www.youtube.com/@{handle}")
        m = re.search(r'"channelId":"(UC[A-Za-z0-9_-]{22})"', html)
        return m.group(1) if m else None
    except Exception:
        return None


def channel_videos(channel_id):
    """RSS로 최근 영상 목록 [(video_id, title, published)]."""
    xml = _get(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
    out = []
    for entry in re.findall(r'<entry>(.*?)</entry>', xml, re.S):
        vid = re.search(r'<yt:videoId>([^<]+)</yt:videoId>', entry)
        title = re.search(r'<title>([^<]+)</title>', entry)
        pub = re.search(r'<published>([^<]+)</published>', entry)
        if vid and title and pub:
            out.append((vid.group(1), title.group(1), pub.group(1)))
    return out


def load(p, default):
    return json.load(open(p)) if os.path.exists(p) else default


def main(resolve=False):
    reg = load(REG, {})
    state = load(STATE, {})           # channel_id -> 마지막 확인 시각(ISO)
    queue = []
    for src in reg.get('sources', []):
        cid = src.get('channel_id')
        if not cid and resolve and src.get('handle'):
            cid = resolve_channel_id(src['handle'])
            if cid:
                src['channel_id'] = cid
                print(f"해결: {src['name']} → {cid}")
            time.sleep(2)
        if not cid:
            print(f"⏭  {src['name']}: channel_id 없음(--resolve 필요 또는 레이트리밋)")
            continue
        last = state.get(cid, '2000-01-01')
        try:
            vids = channel_videos(cid)
        except Exception as e:
            print(f"⚠ {src['name']}: RSS 실패 {str(e)[:40]}")
            continue
        new = [v for v in vids if v[2] > last]
        for vid, title, pub in new:
            queue.append({'video_id': vid, 'title': title, 'published': pub,
                          'source': src['name'], 'domain': src['domain'],
                          'target_skill': src['target_skill'],
                          'url': f"https://www.youtube.com/watch?v={vid}"})
        if vids:
            state[cid] = max(v[2] for v in vids)
        print(f"{'🆕' if new else '  '} {src['name']}: 새 영상 {len(new)}개")
        time.sleep(1)
    if resolve:
        json.dump(reg, open(REG, 'w'), ensure_ascii=False, indent=2)
    json.dump(state, open(STATE, 'w'), ensure_ascii=False, indent=1)
    json.dump(queue, open(QUEUE, 'w'), ensure_ascii=False, indent=1)
    print(f"\n수집 큐: {len(queue)}개 새 영상 → harvest_queue.json")
    if queue:
        print("도메인별:", {d: sum(1 for q in queue if q['domain'] == d)
                          for d in set(q['domain'] for q in queue)})
    return queue


if __name__ == '__main__':
    main(resolve='--resolve' in sys.argv)
