"""Fetch one public reference with Apify; save results without exposing credentials."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
from app.config import DATA, env


def main():
    url = sys.argv[1].split('?')[0]
    video_id = url.rstrip('/').split('/')[-1]
    if not video_id.isdigit() or not url.startswith('https://www.tiktok.com/'):
        raise SystemExit('Expected a full TikTok video URL.')
    folder = DATA / 'references' / video_id
    folder.mkdir(parents=True, exist_ok=True)
    token = env('APIFY_API_TOKEN')
    if not token:
        raise SystemExit('APIFY_API_TOKEN is missing.')
    cap = min(float(env('APIFY_MAX_CHARGE_USD', '0.5')), 0.5)
    base = 'https://api.apify.com/v2'
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        def api(method, path, **kwargs):
            response = client.request(method, base + path,
                headers={'Authorization': 'Bearer ' + token}, **kwargs)
            if response.is_error:
                raise RuntimeError(f'Apify HTTP {response.status_code}')
            return response.json()

        manifest = folder / 'run.json'
        if manifest.exists():
            run = json.loads(manifest.read_text(encoding='utf-8'))
            print('Reusing saved run', run['id'], flush=True)
        else:
            run = api('POST', '/acts/clockworks~tiktok-scraper/runs',
                params={'maxTotalChargeUsd': cap, 'timeout': 180},
                json={'postURLs': [url], 'resultsPerPage': 1,
                      'shouldDownloadVideos': True,
                      'shouldDownloadCovers': False,
                      'shouldDownloadAvatars': False,
                      'downloadSubtitlesOptions': 'NEVER_DOWNLOAD_SUBTITLES'})['data']
            manifest.write_text(json.dumps(run, indent=2), encoding='utf-8')
            print('Started run', run['id'], 'cap USD', cap, flush=True)
        deadline = time.monotonic() + 240
        while True:
            run = api('GET', '/actor-runs/' + run['id'])['data']
            manifest.write_text(json.dumps(run, indent=2), encoding='utf-8')
            print('Status:', run['status'], flush=True)
            if run['status'] not in ('READY', 'RUNNING', 'TIMING-OUT', 'ABORTING'):
                break
            if time.monotonic() > deadline:
                raise SystemExit('Run still active; saved run ID for a later check.')
            time.sleep(10)
        print('Reported charge USD:', run.get('usageTotalUsd', 'unavailable'), flush=True)
        items = api('GET', '/datasets/' + run['defaultDatasetId'] + '/items',
                    params={'format': 'json', 'limit': 1})
        (folder / 'metadata.json').write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding='utf-8')
        if not items:
            print('No dataset items.'); return
        item = items[0]
        print(json.dumps({k: item.get(k) for k in
              ('id', 'text', 'playCount', 'diggCount', 'error', 'errorCode')}, ensure_ascii=False), flush=True)
        print('Video metadata:', json.dumps({k: v for k, v in item.get('videoMeta', {}).items()
              if k in ('duration', 'width', 'height')}, ensure_ascii=False), flush=True)
        media = item.get('mediaUrls') or []
        if isinstance(media, str):
            media = [media]
        if not media:
            records = api('GET', '/key-value-stores/' + run['defaultKeyValueStoreId'] + '/keys')['data']['items']
            media = [base + '/key-value-stores/' + run['defaultKeyValueStoreId'] + '/records/' + record['key']
                     for record in records if record['key'].lower().endswith('.mp4')]
        if not media:
            print('No downloadable video returned.'); return
        for index, address in enumerate(media):
            if not isinstance(address, str) or not address.startswith('https://'):
                continue
            headers = {'Authorization': 'Bearer ' + token} if address.startswith(base + '/') else {}
            with client.stream('GET', address, headers=headers) as response:
                if response.is_error:
                    print('Media download HTTP', response.status_code); continue
                target = folder / ('reference.mp4' if index == 0 else f'reference-{index}.mp4')
                size = 0
                with target.open('wb') as output:
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > 250_000_000:
                            raise RuntimeError('Download exceeds 250 MB.')
                        output.write(chunk)
                print('Downloaded:', str(target), 'bytes:', size, flush=True)


if __name__ == '__main__':
    main()
