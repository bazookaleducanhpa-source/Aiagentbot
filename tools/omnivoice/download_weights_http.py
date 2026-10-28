from pathlib import Path
import httpx,time,hashlib,json,sys,concurrent.futures
sys.stdout.reconfigure(encoding='utf-8');root=Path(__file__).resolve().parents[2]/'.tools/omnivoice-model'
revision='c5fdb5ccb189668d56333f77ba2629f4cd7535f4'
weights=[('model.safetensors',2450344112,'730839316de585f4c8298ec0e1712efc10fb19c6fa4e36eb741cb8d51ebcf6aa'),('audio_tokenizer/model.safetensors',805665628,'fe7c5e8785e0a05833e1bfc3e002ec7f55af21e306b2e7154a448c1f54ccfb0d')]
def fetch(item):
 name,size,expected=item;target=root/name;part=target.with_suffix('.http-part')
 if target.exists() and target.stat().st_size==size:return
 url=f'https://huggingface.co/k2-fsa/OmniVoice/resolve/{revision}/{name}?download=true&cb={time.time()}'
 with httpx.stream('GET',url,follow_redirects=True,timeout=httpx.Timeout(60,connect=20)) as r:
  r.raise_for_status();done=0;mark=0;digest=hashlib.sha256()
  with part.open('wb') as out:
   for chunk in r.iter_bytes(1024*1024):
    out.write(chunk);digest.update(chunk);done+=len(chunk)
    if done-mark>128*1024*1024:print(name,round(done/size*100),'%',flush=True);mark=done
 if done!=size or digest.hexdigest()!=expected:raise RuntimeError(f'Weight verification failed: {name}, {done}, {digest.hexdigest()}')
 part.replace(target);print('VERIFIED',name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(fetch,weights))
print('WEIGHTS_READY',flush=True)
