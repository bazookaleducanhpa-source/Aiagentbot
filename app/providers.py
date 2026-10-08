import json
import base64
from datetime import datetime, timezone, timedelta
import httpx
from .config import env
from . import store

class ProviderError(Exception):
    pass

BUFFER_KEYS = ('BUFFER_API_KEY', 'BUFFER_TIKTOK_CHANNEL_ID', 'CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET')

def request(method, url, **kwargs):
    try:
        response = httpx.request(method, url, timeout=180, **kwargs)
    except httpx.RequestError:
        raise ProviderError('Cannot connect to provider. Check network and configuration.') from None
    if response.is_error:
        # Never expose response bodies / tokens from upstream services.
        raise ProviderError(f'Provider returned HTTP {response.status_code}. Check access, quota and API configuration.')
    return response

def require(*keys):
    missing = [k for k in keys if not env(k)]
    if missing:
        raise ProviderError('Missing configuration: ' + ', '.join(missing))

def generate_json(model, instructions, payload):
    require('OPENAI_API_KEY')
    r = request('POST', 'https://api.openai.com/v1/responses',
        headers={'Authorization': f"Bearer {env('OPENAI_API_KEY')}"},
        json={'model': model, 'instructions': instructions + '\nReturn only a valid JSON object.',
              'input': json.dumps(payload, ensure_ascii=False),
              'text': {'format': {'type': 'json_object'}}, 'max_output_tokens': 5000})
    result = r.json()
    if result.get('status') == 'incomplete':
        raise ProviderError('Model output is incomplete. Try a shorter request or a different model.')
    output = ''.join(x.get('text', '') for item in result.get('output', []) for x in item.get('content', []) if x.get('type') == 'output_text')
    try:
        value = json.loads(output)
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (ValueError, TypeError):
        raise ProviderError('Model returned invalid JSON. Generation stopped; retry after checking the model.') from None

def youtube_search(topic):
    require('YOUTUBE_API_KEY')
    base = 'https://www.googleapis.com/youtube/v3/'
    items = request('GET', base + 'search', params={
        'key': env('YOUTUBE_API_KEY'), 'part': 'snippet', 'q': topic,
        'type': 'video', 'order': 'viewCount', 'maxResults': 12,
        'publishedAfter': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
        'relevanceLanguage': 'en'}).json().get('items', [])
    ids = [x['id']['videoId'] for x in items]
    if not ids:
        return []
    videos = request('GET', base + 'videos', params={
        'key': env('YOUTUBE_API_KEY'), 'part': 'snippet,statistics', 'id': ','.join(ids)}).json().get('items', [])
    return [{'platform': 'youtube', 'url': 'https://www.youtube.com/watch?v=' + v['id'],
             'title': v['snippet']['title'], 'summary': v['snippet'].get('description', '')[:1200],
             'published_at': v['snippet']['publishedAt'], 'views': int(v.get('statistics', {}).get('viewCount', 0)),
             'evidence': 'YouTube API metadata only; video and transcript have not been watched'} for v in videos]

def tiktok_search(topic):
    require('APIFY_API_TOKEN')
    import math
    from urllib.parse import urlparse
    try:
        cap = float(env('APIFY_MAX_CHARGE_USD', '0.5'))
        if not math.isfinite(cap) or not .01 <= cap <= 5:
            raise ValueError()
    except ValueError:
        raise ProviderError('APIFY_MAX_CHARGE_USD must be between 0.01 and 5.') from None
    items = request('POST', 'https://api.apify.com/v2/actors/clockworks~tiktok-scraper/run-sync-get-dataset-items',
        headers={'Authorization': f"Bearer {env('APIFY_API_TOKEN')}"},
        params={'timeout': 120, 'maxTotalChargeUsd': cap, 'restartOnError': False, 'limit': 12},
        json={'searchQueries': [topic], 'resultsPerPage': 12, 'searchSection': '/video',
              'videoSearchDateFilter': 'PAST_WEEK', 'videoSearchSorting': 'MOST_LIKED',
              'shouldDownloadVideos': False, 'shouldDownloadCovers': False,
              'shouldDownloadSubtitles': False, 'shouldDownloadAvatars': False}).json()
    if not isinstance(items, list):
        raise ProviderError('Apify did not return a usable TikTok dataset.')
    sources = []
    for item in items[:12]:
        try:
            url = item['webVideoUrl']
            if urlparse(url).scheme != 'https' or urlparse(url).hostname not in ('www.tiktok.com', 'tiktok.com'):
                continue
            published = datetime.fromisoformat(item['createTimeISO'].replace('Z', '+00:00'))
            if published.tzinfo is None:
                continue
            text = str(item.get('text', ''))
            sources.append({'platform': 'tiktok', 'url': url, 'title': text[:250] or 'TikTok short',
                'summary': text[:1200], 'published_at': published.astimezone(timezone.utc).isoformat(),
                'views': max(0, int(item.get('playCount', 0))),
                'evidence': 'Apify third-party TikTok metadata; video and transcript have not been watched'})
        except (KeyError, TypeError, ValueError):
            continue
    return sources

def score_sources(sources):
    time = datetime.now(timezone.utc)
    scored = []
    # Read the previous snapshot before writing any new observations.
    with store.db() as c:
        for s in {s['url']: s for s in sources}.values():
            published = datetime.fromisoformat(s['published_at'].replace('Z', '+00:00'))
            hours = max(1, (time - published).total_seconds() / 3600)
            prev = c.execute('SELECT views,observed_at FROM observations WHERE url=? ORDER BY observed_at DESC LIMIT 1', (s['url'],)).fetchone()
            growth = None
            if prev:
                elapsed = (time - datetime.fromisoformat(prev['observed_at'])).total_seconds() / 3600
                if elapsed >= 1 / 60 and s['views'] >= prev['views']:
                    growth = round((s['views'] - prev['views']) / elapsed, 1)
            value = dict(s, views_per_hour=round(s['views'] / hours, 1), growth_per_hour=growth)
            scored.append(value)
            c.execute('INSERT INTO observations VALUES(?,?,?)', (s['url'], s['views'], time.isoformat()))
    return sorted(scored, key=lambda x: x['growth_per_hour'] if x['growth_per_hour'] is not None else x['views_per_hour'], reverse=True)[:12]

def speech(text, output, ffmpeg):
    provider = env('TTS_PROVIDER', 'openai')
    if provider == 'elevenlabs':
        require('ELEVENLABS_API_KEY', 'ELEVENLABS_VOICE_ID')
        from urllib.parse import quote
        r = request('POST', 'https://api.elevenlabs.io/v1/text-to-speech/' + quote(env('ELEVENLABS_VOICE_ID'), safe=''),
            headers={'xi-api-key': env('ELEVENLABS_API_KEY')},
            json={'text': text, 'model_id': 'eleven_multilingual_v2'})
        mp3 = output.with_suffix('.mp3')
        mp3.write_bytes(r.content)
        import subprocess
        subprocess.run([ffmpeg, '-y', '-i', str(mp3), '-ar', '24000', '-ac', '1', str(output)], check=True, capture_output=True, timeout=120)
    elif provider == 'groq':
        require('GROQ_API_KEY')
        import subprocess
        import wave
        words = text.split()
        chunks, chunk = [], ''
        for word in words:
            if len(word) > 200:
                raise ProviderError('Groq narration contains a word longer than 200 characters.')
            candidate = (chunk + ' ' + word).strip()
            if len(candidate) > 200:
                chunks.append(chunk)
                chunk = word
            else:
                chunk = candidate
        if chunk:
            chunks.append(chunk)
        if not chunks:
            raise ProviderError('Narration cannot be empty.')
        with wave.open(str(output), 'wb') as combined:
            combined.setnchannels(1)
            combined.setsampwidth(2)
            combined.setframerate(24000)
            for index, chunk in enumerate(chunks):
                r = request('POST', 'https://api.groq.com/openai/v1/audio/speech',
                    headers={'Authorization': f"Bearer {env('GROQ_API_KEY')}"},
                    json={'model': env('GROQ_TTS_MODEL', 'canopylabs/orpheus-v1-english'),
                          'voice': env('GROQ_TTS_VOICE', 'troy'), 'input': chunk, 'response_format': 'wav'})
                raw = output.with_name(f'{output.stem}-groq-{index}.wav')
                raw.write_bytes(r.content)
                try:
                    # Streaming WAV responses may have placeholder lengths; decode actual audio.
                    pcm = subprocess.run([ffmpeg, '-v', 'error', '-i', str(raw), '-f', 's16le',
                        '-ar', '24000', '-ac', '1', 'pipe:1'], check=True, capture_output=True, timeout=120).stdout
                    if not pcm:
                        raise ProviderError('Groq returned empty audio.')
                    combined.writeframes(pcm)
                finally:
                    raw.unlink(missing_ok=True)
    elif provider == 'openai':
        require('OPENAI_API_KEY')
        r = request('POST', 'https://api.openai.com/v1/audio/speech',
            headers={'Authorization': f"Bearer {env('OPENAI_API_KEY')}"},
            json={'model': env('TTS_MODEL', 'gpt-4o-mini-tts'), 'voice': env('TTS_VOICE', 'coral'),
                  'input': text, 'response_format': 'wav',
                  'instructions': 'Narrate in clear, expressive English. Playful storytelling, natural pace.'})
        output.write_bytes(r.content)
    else:
        raise ProviderError('TTS_PROVIDER must be openai, groq or elevenlabs.')

def image(prompt, output):
    require('OPENAI_API_KEY')
    result = request('POST', 'https://api.openai.com/v1/images/generations',
        headers={'Authorization': f"Bearer {env('OPENAI_API_KEY')}"},
        json={'model': env('IMAGE_MODEL', 'gpt-image-2.5-flare'),
              'prompt': 'Original stylized cinematic fantasy illustration. Vertical composition. No text, logos or copyrighted characters. ' + prompt,
              'size': '1024x1536', 'quality': 'low', 'n': 1}).json()
    try:
        output.write_bytes(base64.b64decode(result['data'][0]['b64_json'], validate=True))
    except (KeyError, ValueError, IndexError):
        raise ProviderError('Image provider returned no usable image.') from None

def youtube_upload(video, script, privacy):
    require('YOUTUBE_CLIENT_ID', 'YOUTUBE_CLIENT_SECRET', 'YOUTUBE_REFRESH_TOKEN')
    token = request('POST', 'https://oauth2.googleapis.com/token', data={
        'client_id': env('YOUTUBE_CLIENT_ID'), 'client_secret': env('YOUTUBE_CLIENT_SECRET'),
        'refresh_token': env('YOUTUBE_REFRESH_TOKEN'), 'grant_type': 'refresh_token'}).json()['access_token']
    meta = {'snippet': {'title': script['title'], 'description': script['description'] + '\n\n' + ' '.join(script['hashtags']) + '\nAI-generated visuals.',
                        'categoryId': '24'},
            'status': {'privacyStatus': privacy, 'selfDeclaredMadeForKids': bool(script.get('made_for_kids', False)), 'containsSyntheticMedia': True}}
    init = request('POST', 'https://www.googleapis.com/upload/youtube/v3/videos',
        params={'uploadType': 'resumable', 'part': 'snippet,status'},
        headers={'Authorization': f'Bearer {token}', 'X-Upload-Content-Type': 'video/mp4',
                 'X-Upload-Content-Length': str(video.stat().st_size)}, json=meta)
    location = init.headers.get('Location', '')
    from urllib.parse import urlparse
    parsed = urlparse(location)
    if parsed.scheme != 'https' or parsed.hostname not in {'www.googleapis.com', 'youtube.googleapis.com'}:
        raise ProviderError('YouTube did not return a valid upload URL.')
    with video.open('rb') as f:
        uploaded = request('PUT', location, headers={'Authorization': f'Bearer {token}',
            'Content-Length': str(video.stat().st_size), 'Content-Type': 'video/mp4'}, content=f).json()
    return {'video_id': uploaded['id'], 'url': 'https://www.youtube.com/watch?v=' + uploaded['id'],
            'privacy': uploaded.get('status', {}).get('privacyStatus', privacy)}

def buffer_graphql(query, variables=None):
    require('BUFFER_API_KEY')
    payload = request('POST', 'https://api.buffer.com',
        headers={'Authorization': f"Bearer {env('BUFFER_API_KEY')}"},
        json={'query': query, 'variables': variables or {}}).json()
    if payload.get('errors') or not isinstance(payload.get('data'), dict):
        raise ProviderError('Buffer rejected the API request. Check API access and channel permissions.')
    return payload['data']

def buffer_channels():
    data = buffer_graphql('query DreamforgeOrganizations { account { organizations { id name } } }')
    result = []
    for org in data.get('account', {}).get('organizations', []):
        # JSON quoting is also valid for GraphQL string literals; IDs never become code.
        query = 'query DreamforgeChannels { channels(input: {organizationId: ' + json.dumps(org['id']) + '}) { id name displayName service isQueuePaused isDisconnected isLocked } }'
        channels = buffer_graphql(query).get('channels', [])
        result.extend(dict(channel, organization=org['name']) for channel in channels)
    return result

def cloudinary_upload(video, job_id):
    require('CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET')
    import hashlib
    import time
    from urllib.parse import quote, urlparse
    # The explicit publish action authorizes public hosting of this approved video.
    fields = {'timestamp': str(int(time.time())), 'public_id': f'dreamforge/{job_id}', 'overwrite': 'false'}
    signed = '&'.join(f'{k}={v}' for k,v in sorted(fields.items())) + env('CLOUDINARY_API_SECRET')
    signature = hashlib.sha256(signed.encode()).hexdigest()
    with video.open('rb') as f:
        result = request('POST', 'https://api.cloudinary.com/v1_1/' + quote(env('CLOUDINARY_CLOUD_NAME'), safe='') + '/video/upload',
            data={**fields, 'api_key': env('CLOUDINARY_API_KEY'), 'signature': signature},
            files={'file': (video.name, f, 'video/mp4')}).json()
    url = result.get('secure_url', '')
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname != 'res.cloudinary.com':
        raise ProviderError('Cloudinary did not return a public HTTPS video URL.')
    return url

def buffer_tiktok_publish(video, job, scheduled_at):
    require(*BUFFER_KEYS)
    channel_id = env('BUFFER_TIKTOK_CHANNEL_ID')
    channel = next((c for c in buffer_channels() if c['id'] == channel_id), None)
    if not channel or str(channel.get('service', '')).lower() != 'tiktok':
        raise ProviderError('BUFFER_TIKTOK_CHANNEL_ID does not identify a connected TikTok channel.')
    if channel.get('isQueuePaused'):
        raise ProviderError('Your TikTok queue is paused in Buffer. Resume it before publishing.')
    if channel.get('isDisconnected') or channel.get('isLocked'):
        raise ProviderError('Your TikTok channel is disconnected or locked in Buffer.')
    url = cloudinary_upload(video, job['id'])
    script = job['script']
    hashtags = job.get('spec', {}).get('tiktok_hashtags', script['hashtags'])
    text = script['title'] + '\n\n' + script['description'] + '\n' + ' '.join(hashtags)
    query = '''mutation DreamforgeTikTok($input: CreatePostInput!) {
      createPost(input: $input) {
        __typename
        ... on PostActionSuccess { post { id status dueAt } }
        ... on MutationError { message }
      }
    }'''
    due = datetime.fromisoformat(scheduled_at).astimezone(timezone.utc)
    # Local jobs submit at their due time. Give Buffer a minute to ingest the video.
    due = max(due, datetime.now(timezone.utc) + timedelta(minutes=1))
    data = buffer_graphql(query, {'input': {
        'channelId': channel_id, 'text': text, 'schedulingType': 'automatic',
        'mode': 'customScheduled', 'dueAt': due.isoformat(),
        'needsApproval': False, 'saveToDraft': False, 'aiAssisted': True,
        'metadata': {'tiktok': {'isAiGenerated': True}},
        'assets': [{'video': {'url': url, 'metadata': {'thumbnailOffset': 1000}}}]
    }})
    action = data.get('createPost', {})
    post = action.get('post')
    if action.get('__typename') != 'PostActionSuccess' or not post or not post.get('id'):
        raise ProviderError('Buffer did not confirm post creation. Check Buffer before attempting another post.')
    return {'provider': 'buffer', 'post_id': post['id'], 'remote_status': post.get('status'),
            'due_at': post.get('dueAt'), 'media_url': url, 'url': 'https://publish.buffer.com/',
            'message': 'Submitted to Buffer for automatic TikTok publishing. This does not yet confirm a live TikTok post.'}

def buffer_post_status(post_id):
    data = buffer_graphql('query DreamforgePost { post(input: {id: ' + json.dumps(post_id) + '}) { id status } }')
    post = data.get('post')
    if not post:
        raise ProviderError('Buffer post was not found. Check your Buffer account.')
    return post['status']

def buffer_post_details(post_id):
    data = buffer_graphql('query DreamforgePostDetails { post(input: {id: ' + json.dumps(post_id) +
        '}) { id status externalLink error { message supportUrl } } }')
    post = data.get('post')
    if not post:
        raise ProviderError('Buffer post was not found. Check your Buffer account.')
    return post
