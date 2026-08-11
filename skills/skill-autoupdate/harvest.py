"""
자막 수집기 — harvest_queue.json의 새 영상 자막을 yt-dlp로 다운로드(재시도 파도).

yt-dlp는 봇 차단(429)을 자주 낸다 — 이 세션에서 검증된 회복법: 실패 시 대기 후 재시도.
자막만 받고(영상 X), 추출·스킬반영은 루틴의 Claude가 수행(서브에이전트로 인사이트 추출).

사용: python harvest.py [--max N] [--wait 300]
결과: transcripts/<domain>/<video_id>.txt + harvest_queue.json에서 done 표시
"""
import os, sys, json, subprocess, glob, time, re

HERE = os.path.dirname(__file__)
QUEUE = os.path.join(HERE, 'harvest_queue.json')
TDIR = os.path.join(HERE, 'transcripts')


def vtt_to_text(path):
    lines, seen = [], set()
    for ln in open(path, encoding='utf-8', errors='replace'):
        ln = ln.strip()
        if not ln or '-->' in ln or ln.startswith(('WEBVTT', 'Kind:', 'Language:')) or ln.isdigit():
            continue
        ln = re.sub(r'<[^>]+>', '', ln)
        if ln and ln not in seen:
            seen.add(ln); lines.append(ln)
    return ' '.join(lines)


def harvest_one(item):
    d = os.path.join(TDIR, item['domain']); os.makedirs(d, exist_ok=True)
    out = os.path.join(d, item['video_id'])
    txt = out + '.txt'
    if os.path.exists(txt):
        return True
    r = subprocess.run(['yt-dlp', '--skip-download', '--write-auto-sub', '--sub-lang', 'en,ko',
                        '--sub-format', 'vtt', '-o', out, item['url']],
                       capture_output=True, text=True, timeout=120)
    vtts = glob.glob(out + '*.vtt')
    if vtts:
        open(txt, 'w', encoding='utf-8').write(vtt_to_text(vtts[0]))
        for v in vtts: os.remove(v)
        return True
    return False


def main(max_n=20, wait=300):
    queue = json.load(open(QUEUE))
    todo = [q for q in queue if not q.get('done')]
    done, failed = 0, []
    for item in todo[:max_n]:
        ok = False
        for attempt in range(2):
            try:
                ok = harvest_one(item)
            except Exception:
                ok = False
            if ok: break
            if attempt == 0:
                print(f"  재시도 대기 {wait}s: {item['title'][:40]}", flush=True)
                time.sleep(wait)
        item['done'] = ok
        if ok: done += 1
        else: failed.append(item['title'][:40])
        print(f"{'✅' if ok else '❌'} [{item['domain']}] {item['title'][:50]}", flush=True)
        time.sleep(5)
    json.dump(queue, open(QUEUE, 'w'), ensure_ascii=False, indent=1)
    print(f"\n수집 완료 {done}개 / 실패 {len(failed)}개. 남은 큐: {sum(1 for q in queue if not q.get('done'))}")
    print(f"자막 → {TDIR}/<domain>/. 다음: 루틴이 이 자막에서 인사이트 추출→스킬 갱신.")


if __name__ == '__main__':
    mx = int(sys.argv[sys.argv.index('--max')+1]) if '--max' in sys.argv else 20
    wt = int(sys.argv[sys.argv.index('--wait')+1]) if '--wait' in sys.argv else 300
    main(mx, wt)
