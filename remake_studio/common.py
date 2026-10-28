from pathlib import Path
import json, os, shutil, subprocess, sys, threading

ROOT=Path(__file__).resolve().parents[1]
JOBS=ROOT/'data/remake-jobs'; JOBS.mkdir(parents=True,exist_ok=True)
LOCK=threading.RLock()
STAGES=[('source','Phân tích nguồn'),('research','Nghiên cứu & kiểm chứng'),('script','Biên kịch'),('visuals','Đạo diễn hình ảnh'),('voice','Giọng đọc'),('sound','Nhạc & hiệu ứng'),('qa','Kiểm tra'),('export','Xuất video')]
DEFAULTS={'language':'en','subtitles':False,'on_screen_text':True,'text_policy':'section-titles-and-entity-labels-only','visual_beat_seconds':[3,6],'animation':'continuous-causal-actions','art':'soft-rounded-organic','media':'curated-real-media-when-relevant','music':'upbeat-existing-library','mascot':'white-capybara','humor':'restrained'}

def write_json(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with LOCK:
        temp=path.with_suffix(path.suffix+'.tmp'); temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); temp.replace(path)

def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def run(args,*,cwd=ROOT,timeout=600,input=None,log=None):
    env={**os.environ,'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8'}
    env['PATH']=str(ROOT/'.tools/ffmpeg/ffmpeg-9.0.2-full_build/bin')+os.pathsep+env.get('PATH','')
    result=subprocess.run([str(a) for a in args],cwd=cwd,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,env=env,encoding='utf-8',errors='replace',creationflags=0x08000000 if os.name=='nt' else 0)
    if log: Path(log).write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError(f'{Path(str(args[0])).name} failed: '+result.stderr[-1800:])
    return result.stdout

def codex_path():
    candidates=list(Path('C:/nvm4w/nodejs/node_modules/@openai/codex').glob('**/bin/codex.exe'))
    return str(candidates[0]) if candidates else shutil.which('codex')

def probe(path):
    return read_probe(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',path]))

def read_probe(text):return json.loads(text)

def update(job,stage,status='running',detail='',**extra):
    with LOCK:
        data=read_json(job/'job.json'); data.update(stage=stage,status='running',**extra)
        for s in data['stages']:
            if s['id']==stage:s.update(status=status,detail=detail)
        data['progress']=round(100*sum(s['status']=='complete' for s in data['stages'])/len(STAGES))
        write_json(job/'job.json',data)
