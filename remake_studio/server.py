import importlib.util,json,re,shutil,threading,uuid
from datetime import datetime,timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from .common import ROOT,JOBS,STAGES,DEFAULTS,read_json,write_json,codex_path
from .source import video_id
from .pipeline import JobAlreadyRunning, job_lock, is_job_running

app=FastAPI(title='Cappy Remake Studio')
pool=ThreadPoolExecutor(max_workers=1)
pending=set(); guard=threading.Lock()
class NewJob(BaseModel):
    url:str=Field(max_length=2048)
    language:str='en'
    notes:str=Field(default='',max_length=6000)

@app.middleware('http')
async def local_only(request:Request,call_next):
    origin=request.headers.get('origin','')
    if request.method not in ('GET','HEAD','OPTIONS') and origin and origin not in ('http://127.0.0.1:8010','http://localhost:8010'):
        from fastapi.responses import JSONResponse
        return JSONResponse({'detail':'Local requests only'},status_code=403)
    return await call_next(request)

def job_path(job_id):
    if not re.fullmatch(r'[a-f0-9]{12}',job_id):raise HTTPException(404,'Job không tồn tại')
    path=JOBS/job_id
    if not (path/'job.json').exists():raise HTTPException(404,'Job không tồn tại')
    return path

def public_job(path):
    d=read_json(path/'job.json')
    for field,name in [('video_url','final.mp4'),('audio_url','full-mix.mp3')]:
        ready=d['status']=='complete' if field=='video_url' else any(s['id']=='sound' and s['status']=='complete' for s in d.get('stages',[]))
        d[field]=f'/api/jobs/{d["id"]}/files/{name}' if ready and (path/'deliverables'/name).exists() else None
    d['preview_url']=d['video_url']
    d['credits_url']=f'/api/jobs/{d["id"]}/files/credits.txt' if (path/'deliverables/credits.txt').is_file() else None
    for field,name in [('thumbnail_url','thumbnail.jpg'),('title_url','title.txt')]:
        d[field]=f'/api/jobs/{d["id"]}/files/{name}' if (path/'deliverables'/name).is_file() else None
    return d

def submit(path):
    with guard:
        if path.name in pending:raise HTTPException(409,'Job đang chạy')
        pending.add(path.name)
    def work():
        try:
            from .pipeline import execute
            execute(path)
        except JobAlreadyRunning:
            pass  # The active CLI/server owner alone may update this job.
        except Exception as e:
            d=read_json(path/'job.json');d.update(status='failed',error=str(e)[:2000])
            for st in d['stages']:
                if st['status']=='running':st.update(status='failed',detail=str(e)[:400])
            write_json(path/'job.json',d)
        finally:
            with guard:pending.discard(path.name)
    pool.submit(work)

@app.get('/api/status')
def status():
    caps={k:bool(importlib.util.find_spec(k)) for k in ('yt_dlp','edge_tts')}
    caps.update(ffmpeg=bool(shutil.which('ffmpeg')),codex=bool(codex_path()))
    return {'ready':all(caps.values()),'capabilities':caps,'defaults':DEFAULTS}

@app.get('/api/jobs')
def jobs():return {'jobs':sorted([public_job(p.parent) for p in JOBS.glob('*/job.json')],key=lambda d:d['created_at'],reverse=True)}

@app.post('/api/jobs')
def create(body:NewJob):
    try:vid=video_id(body.url)
    except ValueError as e:raise HTTPException(422,str(e))
    if body.language not in ('en','vi'):raise HTTPException(422,'Ngôn ngữ hỗ trợ: en, vi')
    if body.language!='en':raise HTTPException(422,'Pipeline hiện dùng giọng/kịch bản tiếng Anh; chọn English.')
    with guard:
        if len(pending)>=3:raise HTTPException(429,'Đã có 3 job trong hàng chờ')
    jid=uuid.uuid4().hex[:12];path=JOBS/jid;path.mkdir()
    data={'id':jid,'url':'https://www.youtube.com/watch?v='+vid,'title':vid,'status':'queued','stage':'source','progress':0,'created_at':datetime.now(timezone.utc).isoformat(),'error':None,'notes':body.notes,'language':body.language,'stages':[{'id':k,'label':v,'status':'pending','detail':''} for k,v in STAGES]}
    write_json(path/'job.json',data);submit(path);return public_job(path)

@app.get('/api/jobs/{jid}')
def get_job(jid:str):return public_job(job_path(jid))

@app.post('/api/jobs/{jid}/retry')
def retry(jid:str):
    path=job_path(jid)
    try:
        with job_lock(path):
            d=read_json(path/'job.json')
            if d['status'] not in ('failed','interrupted'):raise HTTPException(409,'Chỉ chạy lại job bị lỗi/gián đoạn')
            d.update(status='queued',error=None);write_json(path/'job.json',d)
    except JobAlreadyRunning:
        raise HTTPException(409,'Job đang được xử lý trong tiến trình khác')
    submit(path);return public_job(path)

@app.get('/api/jobs/{jid}/files/{name}')
def artifact(jid:str,name:str):
    if name not in ('final.mp4','full-mix.mp3','manifest.json','qa.json','credits.txt','thumbnail.jpg','title.txt'):raise HTTPException(404)
    path=job_path(jid)/'deliverables'/name
    if not path.is_file():raise HTTPException(404)
    return FileResponse(path,media_type={'mp4':'video/mp4','mp3':'audio/mpeg','json':'application/json','txt':'text/plain','jpg':'image/jpeg'}[path.suffix[1:]],filename=name)

@app.get('/api/assets/music')
def music():return {'tracks':[{'name':p.name} for p in (ROOT/'assets/music').glob('*.mp3')]}

@app.get('/')
def home():return FileResponse(ROOT/'remake_web/index.html')

app.mount('/static',StaticFiles(directory=ROOT/'remake_web',check_dir=False),name='static')

@app.on_event('startup')
def recover():
    for p in JOBS.glob('*/job.json'):
        try:
            with job_lock(p.parent):
                d=read_json(p)
                if d.get('status') in ('queued','running'):
                    message='Ứng dụng đã dừng giữa chừng. Bấm chạy lại để tiếp tục từ cache.'
                    d.update(status='interrupted',error=message)
                    for stage in d.get('stages',[]):
                        if stage.get('status')=='running':stage.update(status='interrupted',detail=message)
                    write_json(p,d)
        except JobAlreadyRunning:
            continue
