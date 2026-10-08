import json
import threading
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Literal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from . import store, pipeline
from .config import ROOT, ARTIFACTS, demo, env
from .models import Campaign, Script, SourceInput, Publication, Feedback

@asynccontextmanager
async def lifespan(app):
    store.init()
    stop = threading.Event()
    thread = threading.Thread(target=pipeline.scheduler, args=(stop,), daemon=True)
    thread.start()
    yield
    stop.set()
    thread.join(timeout=2)

app = FastAPI(title='Dreamforge Studio', lifespan=lifespan)

@app.middleware('http')
async def local_only(request: Request, call_next):
    # Local tool: reject DNS rebinding and cross-origin mutations.
    if request.url.hostname not in ('127.0.0.1', 'localhost', 'testserver', '::1'):
        return JSONResponse({'detail': 'Run this local app on localhost.'}, status_code=403)
    origin = request.headers.get('origin')
    if request.method not in ('GET', 'HEAD', 'OPTIONS') and origin and origin != str(request.base_url).rstrip('/'):
        return JSONResponse({'detail': 'Cross-origin writes are not allowed.'}, status_code=403)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response

def find_job(job_id):
    j = store.job(job_id)
    if not j:
        raise HTTPException(404, 'Job not found.')
    return j

def editable(j):
    if j['status'] not in ('review', 'approved', 'failed'):
        raise HTTPException(409, 'Wait for the current generation to finish.')
    with store.db() as c:
        sent = c.execute("SELECT 1 FROM publications WHERE job_id=? AND status IN ('sending','published','unknown','submitted','remote_error')", (j['id'],)).fetchone()
    if sent:
        raise HTTPException(409, 'An upload has started. Create a new job for a different version.')

def cancel_pending(job_id):
    with store.db() as c:
        c.execute("UPDATE publications SET status='cancelled' WHERE job_id=? AND status='queued'", (job_id,))

@app.get('/')
def index():
    return FileResponse(ROOT / 'web' / 'index.html')

@app.get('/setup-guide')
def setup_guide():
    return FileResponse(ROOT / 'docs' / 'API_SETUP_VI.md', filename='API_SETUP_VI.md')

@app.get('/api/settings')
def settings():
    return {'mode': 'demo' if demo() else 'live', 'language': 'English',
        'content_model': env('CONTENT_MODEL', 'gpt-6.1-sol'), 'research_model': env('RESEARCH_MODEL', 'gpt-6-luna'),
        'image_model': env('IMAGE_MODEL', 'gpt-image-2.5-flare'), 'tts_provider': env('TTS_PROVIDER', 'openai'),
        'tiktok_publisher': env('TIKTOK_PUBLISHER', 'manual'),
        'connections': {'openai': bool(env('OPENAI_API_KEY')), 'youtube_research': bool(env('YOUTUBE_API_KEY')),
            'tiktok_research': bool(env('APIFY_API_TOKEN')),
            'youtube_upload': all(env(k) for k in ('YOUTUBE_CLIENT_ID', 'YOUTUBE_CLIENT_SECRET', 'YOUTUBE_REFRESH_TOKEN')),
            'elevenlabs': bool(env('ELEVENLABS_API_KEY') and env('ELEVENLABS_VOICE_ID')),
            'tiktok': all(env(k) for k in ('BUFFER_API_KEY', 'BUFFER_TIKTOK_CHANNEL_ID', 'CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET'))}}

@app.get('/api/jobs')
def jobs():
    with store.db() as c:
        return [store.decode(r) for r in c.execute('SELECT * FROM jobs ORDER BY created_at DESC LIMIT 100')]

@app.post('/api/jobs', status_code=201)
def create_job(spec: Campaign):
    if not demo():
        from .providers import require, ProviderError
        try:
            require('OPENAI_API_KEY')
            if env('TTS_PROVIDER', 'openai') == 'elevenlabs':
                require('ELEVENLABS_API_KEY', 'ELEVENLABS_VOICE_ID')
        except ProviderError as e:
            raise HTTPException(400, str(e))
    job_id = uuid.uuid4().hex
    with store.db() as c:
        count = c.execute("SELECT count(*) FROM jobs WHERE status IN ('queued','researching','writing','producing')").fetchone()[0]
        if count >= 4:
            raise HTTPException(429, 'Four jobs are already queued. Wait before creating another.')
        c.execute('INSERT INTO jobs(id,topic,spec,mode,status,created_at) VALUES(?,?,?,?,?,?)',
            (job_id, spec.topic, spec.model_dump_json(), 'demo' if demo() else 'live', 'queued', store.now()))
    store.event(job_id, 'queue', 'Queued for the four-agent workflow.')
    pipeline.executor.submit(pipeline.run, job_id)
    return find_job(job_id)

@app.get('/api/jobs/{job_id}')
def detail(job_id: str):
    return find_job(job_id)

@app.post('/api/jobs/{job_id}/retry')
def retry(job_id: str):
    with pipeline.publication_lock:
        j = find_job(job_id)
        editable(j)
        if j['status'] != 'failed':
            raise HTTPException(409, 'Only failed jobs can be retried.')
        cancel_pending(job_id)
        store.update(job_id, status='queued', error=None, artifacts=None, approved=0)
        pipeline.executor.submit(pipeline.run, job_id)
    return find_job(job_id)

@app.put('/api/jobs/{job_id}/script')
def edit_script(job_id: str, script: Script):
    with pipeline.publication_lock:
        j = find_job(job_id)
        editable(j)
        cancel_pending(job_id)
        store.update(job_id, script=script.model_dump(), status='producing', artifacts=None, approved=0)
        store.event(job_id, 'content', 'Script edited. Previous approval revoked; rendering a new version.')
        pipeline.executor.submit(pipeline.run, job_id, True)
    return find_job(job_id)

@app.post('/api/jobs/{job_id}/approve')
def approve(job_id: str):
    with pipeline.publication_lock:
        j = find_job(job_id)
        if j['status'] not in ('review', 'approved') or not j.get('artifacts'):
            raise HTTPException(409, 'A rendered video must be ready for review.')
        store.update(job_id, approved=1, status='approved')
        store.event(job_id, 'review', 'Current video approved by the owner.')
    return find_job(job_id)

@app.post('/api/jobs/{job_id}/publish', status_code=201)
def publish(job_id: str, publication: Publication):
    with pipeline.publication_lock:
        j = find_job(job_id)
        if not j['approved'] or j['status'] != 'approved':
            raise HTTPException(409, 'Preview and approve this version first.')
        if publication.platform not in j['spec']['platforms']:
            raise HTTPException(400, 'Platform was not selected for this job.')
        provider = 'native'
        if publication.platform == 'tiktok':
            provider = publication.tiktok_mode or env('TIKTOK_PUBLISHER', 'manual')
            if provider not in ('manual', 'buffer'):
                raise HTTPException(400, 'TIKTOK_PUBLISHER must be manual or buffer.')
            if provider == 'buffer' and j['mode'] == 'live':
                if publication.privacy != 'public':
                    raise HTTPException(400, 'Buffer publishing uploads this video to public media hosting. Select Public to confirm this destination.')
                from .providers import require, ProviderError, BUFFER_KEYS
                try:
                    require(*BUFFER_KEYS)
                except ProviderError as e:
                    raise HTTPException(400, str(e))
        if j['mode'] == 'live' and publication.platform == 'youtube':
            from .providers import require, ProviderError
            try:
                require('YOUTUBE_CLIENT_ID', 'YOUTUBE_CLIENT_SECRET', 'YOUTUBE_REFRESH_TOKEN')
            except ProviderError as e:
                raise HTTPException(400, str(e))
        with store.db() as c:
            existing = c.execute('SELECT status FROM publications WHERE job_id=? AND platform=?', (job_id, publication.platform)).fetchone()
            if existing and existing['status'] != 'cancelled':
                raise HTTPException(409, 'This platform already has a publication entry.')
            c.execute('''INSERT INTO publications(job_id,platform,status,scheduled_at,privacy,created_at,provider)
                VALUES(?,?,?,?,?,?,?) ON CONFLICT(job_id,platform) DO UPDATE SET
                status=excluded.status, scheduled_at=excluded.scheduled_at, privacy=excluded.privacy,
                provider=excluded.provider, result=NULL''',
                (job_id, publication.platform, 'queued', publication.scheduled_at or store.now(), publication.privacy, store.now(), provider))
        store.event(job_id, 'publisher', f'{publication.platform} added to the publication queue.')
    return find_job(job_id)

@app.post('/api/publications/{publication_id}/cancel')
def cancel_publication(publication_id: int):
    with pipeline.publication_lock, store.db() as c:
        changed = c.execute("UPDATE publications SET status='cancelled' WHERE id=? AND status='queued'", (publication_id,)).rowcount
        if not changed:
            raise HTTPException(409, 'Only queued publications can be cancelled.')
    return {'ok': True}

@app.post('/api/publications/{publication_id}/sync')
def sync_publication(publication_id: int):
    from .providers import buffer_post_status, ProviderError
    with pipeline.publication_lock:
        with store.db() as c:
            row = c.execute('SELECT * FROM publications WHERE id=?', (publication_id,)).fetchone()
        if not row or row['provider'] != 'buffer' or row['status'] not in ('submitted', 'published', 'remote_error'):
            raise HTTPException(409, 'Only confirmed Buffer entries can be synchronized.')
        result = json.loads(row['result'])
        try:
            remote = buffer_post_status(result['post_id'])
        except ProviderError as e:
            raise HTTPException(400, str(e))
        status = 'published' if remote == 'sent' else 'remote_error' if remote == 'error' else 'submitted'
        result['remote_status'] = remote
        result['message'] = 'Buffer reports: ' + remote + '. Check Buffer for post details.'
        with store.db() as c:
            c.execute('UPDATE publications SET status=?,result=? WHERE id=?', (status, json.dumps(result), publication_id))
        return {'status': status, 'result': result}

@app.post('/api/jobs/{job_id}/feedback')
def feedback(job_id: str, value: Feedback):
    j = find_job(job_id)
    if not j.get('script') or j['status'] not in ('review', 'approved'):
        raise HTTPException(409, 'Feedback requires a finished script and video.')
    store.update(job_id, feedback=value.model_dump())
    store.event(job_id, 'learning', 'Performance feedback saved for future content prompts.')
    return find_job(job_id)

@app.get('/api/sources')
def sources():
    with store.db() as c:
        return [dict(id=r['id'], **json.loads(r['payload'])) for r in c.execute('SELECT * FROM sources ORDER BY id DESC LIMIT 100')]

@app.post('/api/sources', status_code=201)
def add_source(value: SourceInput):
    with store.db() as c:
        # Update imported stats rather than keeping competing snapshots of the same source.
        rows = c.execute('SELECT id,payload FROM sources').fetchall()
        existing = next((r['id'] for r in rows if json.loads(r['payload'])['url'] == value.url), None)
        if existing:
            c.execute('UPDATE sources SET payload=?,created_at=? WHERE id=?', (value.model_dump_json(), store.now(), existing))
        else:
            c.execute('INSERT INTO sources(payload,created_at) VALUES(?,?)', (value.model_dump_json(), store.now()))
    return {'ok': True}

@app.delete('/api/sources/{source_id}')
def delete_source(source_id: int):
    with store.db() as c:
        c.execute('DELETE FROM sources WHERE id=?', (source_id,))
    return {'ok': True}

class SkillEdit(BaseModel):
    body: str = Field(min_length=10, max_length=10000)

@app.get('/api/skills')
def skills():
    return {name: pipeline.skill(name) for name in ('research', 'content', 'production', 'publisher')}

@app.put('/api/skills/{name}')
def edit_skill(name: Literal['research', 'content'], value: SkillEdit):
    with store.db() as c:
        c.execute('INSERT INTO skills VALUES(?,?) ON CONFLICT(name) DO UPDATE SET body=excluded.body', (name, value.body))
    return {'ok': True}

@app.get('/artifacts/{job_id}/{filename}')
def artifact(job_id: str, filename: str):
    allowed = {'video.mp4', 'cover.png', 'publish-kit.zip', 'captions.srt', 'caption.txt', 'script.json', 'research.json'}
    if filename not in allowed or len(job_id) != 32 or any(c not in '0123456789abcdef' for c in job_id):
        raise HTTPException(404, 'Artifact not found.')
    path = ARTIFACTS / job_id / filename
    if not path.is_file():
        raise HTTPException(404, 'Artifact not found.')
    return FileResponse(path, filename=filename if filename.endswith(('.zip', '.srt', '.json', '.txt')) else None)

app.mount('/static', StaticFiles(directory=ROOT / 'web'), name='static')
