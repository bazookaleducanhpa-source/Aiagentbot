import json
import threading
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError
from . import store, providers, media
from .config import ROOT, ARTIFACTS, env
from .models import Script

executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='agent')
publication_lock = threading.Lock()

def skill(name):
    with store.db() as c:
        row = c.execute('SELECT body FROM skills WHERE name=?', (name,)).fetchone()
    return row['body'] if row else (ROOT / 'skills' / f'{name}.md').read_text(encoding='utf-8')

def feedback_context():
    with store.db() as c:
        rows = c.execute("SELECT topic,script,feedback FROM jobs WHERE feedback IS NOT NULL AND mode='live' ORDER BY created_at DESC LIMIT 8").fetchall()
    return [{'topic': r['topic'], 'title': json.loads(r['script'])['title'], 'feedback': json.loads(r['feedback'])} for r in rows]

def research(job):
    if job['mode'] == 'demo':
        # Synthetic examples deliberately have no real video links or claimed popularity.
        return {'sources': [], 'summary': 'Demo mode: no live sources collected and no trend verified.',
                'angles': [f"An original short story inspired by {job['topic']}", 'A tiny hero with an unexpected superpower'], 'demo': True}
    with store.db() as c:
        imported = [json.loads(r['payload']) for r in c.execute('SELECT payload FROM sources ORDER BY id DESC LIMIT 30')]
    fetched = providers.youtube_search(job['topic']) if env('YOUTUBE_API_KEY') else []
    if env('APIFY_API_TOKEN'):
        fetched += providers.tiktok_search(job['topic'])
    sources = providers.score_sources(fetched + imported)
    result = providers.generate_json(env('RESEARCH_MODEL', 'gpt-6-luna'), skill('research') +
        '\nJSON schema: {"summary":string,"angles":[string]}. With no sources, explicitly state no trend has been verified.',
        {'topic': job['topic'], 'audience': job['spec']['audience'], 'sources': sources})
    if not isinstance(result.get('summary'), str) or not isinstance(result.get('angles'), list) or not all(isinstance(x, str) for x in result['angles']):
        raise providers.ProviderError('Research returned an invalid structure.')
    return {'sources': sources, 'summary': result['summary'], 'angles': result['angles'], 'demo': False}

def demo_script(job):
    topic = job['topic']
    hero = 'A tiny round silver robot with teal eyes and a mustard-yellow scarf'
    return Script(title=f'{topic[:65]}: a tiny unexpected adventure',
        description='A fictional sample story for the Dreamforge demo. Live mode creates AI-generated visuals and English narration.',
        hashtags=['#AIArt', '#AIStories', '#Shorts'], scenes=[
            {'heading': 'The door that was not there', 'narration': f'In a world inspired by {topic[:100]}, a tiny robot found a glowing door. It had never been there before. Behind it, something was humming.', 'visual': hero + ' discovers a glowing door in a surreal moonlit forest.'},
            {'heading': 'A sky full of lost stars', 'narration': 'Beyond the door floated hundreds of sleepy stars. One little star had forgotten how to shine. The robot held out its warm yellow scarf.', 'visual': hero + ' meets a small dim star in a floating celestial garden.'},
            {'heading': 'One small spark', 'narration': 'The star wrapped itself in the scarf. First came a spark. Then a gentle glow. Suddenly, every sleeping star woke up and began to dance.', 'visual': hero + ' watches a little star wrapped in its yellow scarf light up a glowing galaxy.'},
            {'heading': 'A light to take home', 'narration': 'When the robot returned, the door was gone. But a little star followed it home. Sometimes, the smallest kindness lights up an entire universe.', 'visual': hero + ' walks home beneath a tiny friendly glowing star, surreal twilight landscape.'}
        ]).model_dump()

def write(job):
    if job['mode'] == 'demo':
        return demo_script(job)
    schema = Script.model_json_schema()
    raw = providers.generate_json(env('CONTENT_MODEL', 'gpt-6.1-sol'), skill('content') + '\nOutput JSON must match this schema: ' + json.dumps(schema),
        {'brief': job['spec'], 'research': job['research'], 'recent_performance': feedback_context()})
    try:
        return Script.model_validate(raw).model_dump()
    except ValidationError:
        raise providers.ProviderError('Script is invalid or too long. Adjust the content skill and retry.') from None

def run(job_id, production_only=False):
    try:
        j = store.job(job_id)
        if not production_only:
            store.update(job_id, status='researching', error=None, approved=0)
            store.event(job_id, 'research', 'Collecting and analyzing source evidence.')
            result = research(j)
            store.update(job_id, research=result, status='writing')
            store.event(job_id, 'content', 'Writing an English story using channel skills and recent feedback.')
            j = store.job(job_id)
            store.update(job_id, script=write(j))
        store.update(job_id, status='producing', approved=0)
        j = store.job(job_id)
        result = media.render(j, lambda m: store.event(job_id, 'production', m))
        store.update(job_id, artifacts=result, status='review')
        store.event(job_id, 'review', 'Video is ready. Preview and approve before queuing publication.')
    except Exception as e:
        if isinstance(e, providers.ProviderError):
            message = str(e)
        elif isinstance(e, subprocess_error()):
            message = 'FFmpeg render failed. Check FFmpeg and data directory permissions.'
        else:
            message = f'Internal error ({type(e).__name__}). Check configuration and retry.'
        store.update(job_id, status='failed', error=message, approved=0)
        store.event(job_id, 'error', message)

def subprocess_error():
    import subprocess
    return (subprocess.CalledProcessError, subprocess.TimeoutExpired)

def dispatch_publications():
    if not publication_lock.acquire(blocking=False):
        return
    try:
        with store.db() as c:
            entries = [dict(r) for r in c.execute("SELECT * FROM publications WHERE status='queued' AND scheduled_at <= ? ORDER BY id", (store.now(),))]
        for entry in entries:
            j = store.job(entry['job_id'])
            if not j or not j['approved'] or j['status'] != 'approved':
                with store.db() as c:
                    c.execute("UPDATE publications SET status='cancelled', result=? WHERE id=?", (json.dumps({'message': 'Video is not approved.'}), entry['id']))
                continue
            with store.db() as c:
                claimed = c.execute("UPDATE publications SET status='sending' WHERE id=? AND status='queued'", (entry['id'],)).rowcount
            if not claimed:
                continue
            try:
                if entry['platform'] == 'tiktok' and entry['provider'] != 'buffer':
                    status, result = 'manual', {'message': 'Download the publish kit and complete posting in TikTok.', 'kit': j['artifacts']['kit']}
                elif j['mode'] == 'demo':
                    status, result = 'simulated', {'message': 'Demo: simulated queue only. Nothing was posted externally.'}
                elif entry['platform'] == 'tiktok':
                    result = providers.buffer_tiktok_publish(ARTIFACTS / j['id'] / 'video.mp4', j, entry['scheduled_at'])
                    status = 'submitted'
                else:
                    result = providers.youtube_upload(ARTIFACTS / j['id'] / 'video.mp4', j['script'], entry['privacy'])
                    status = 'published'
                with store.db() as c:
                    c.execute('UPDATE publications SET status=?,result=? WHERE id=?', (status, json.dumps(result, ensure_ascii=False), entry['id']))
                store.event(j['id'], 'publisher', f"{entry['platform']}: {status}")
            except Exception:
                # An interrupted upload may have succeeded upstream; never auto-retry.
                with store.db() as c:
                    c.execute("UPDATE publications SET status='unknown',result=? WHERE id=?", (json.dumps({'message': 'Upload result is uncertain. Check the provider dashboard (YouTube Studio or Buffer). No automatic retry.'}), entry['id']))
                store.event(j['id'], 'publisher', 'Upload result is uncertain. Check the platform before retrying.')
    finally:
        publication_lock.release()

def scheduler(stop):
    while not stop.is_set():
        try:
            dispatch_publications()
        except Exception:
            # Keep scheduling future entries even if a transient database error occurs.
            pass
        stop.wait(5)
