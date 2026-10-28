from pathlib import Path
import asyncio,hashlib,json,math,os,re,shutil,subprocess,sys,wave,xml.etree.ElementTree as ET
import edge_tts
from .common import ROOT,run,write_json,read_json,probe

FPS=30
SR=24000
def validate_visuals(visuals,script):
    expected={s['id'] for s in script['scenes']}
    if {s['id'] for s in visuals['scenes']}!=expected:raise ValueError('Visual scene IDs do not match narration')
    allowed={'g','path','rect','circle','ellipse','line','polyline','polygon','defs','linearGradient','radialGradient','stop','clipPath','mask','use'}
    count=0
    for scene in visuals['scenes']:
        entities={}
        if not 2<=len(scene['beats'])<=5:raise ValueError(f'{scene["id"]}: need 2–5 visual beats')
        for b in scene['beats']:
            if not re.fullmatch(r'#[0-9a-fA-F]{6}',b['background']):raise ValueError('Invalid background color')
            if not 2<=len(b['layers'])<=10:raise ValueError('Visual beat needs coherent multi-layer illustration')
            for label in b.get('labels',[]):
                if not 1<=len(label['text'].split())<=4 or len(label['text'])>50:raise ValueError('Entity labels need short identifying names')
                if label['target_entity_id'] not in {l.get('entity_id') for l in b['layers']}:raise ValueError('Label target must exist in its beat')
                if not all(math.isfinite(float(label[k])) for k in ('x','y','from','duration')) or label['from']<0 or label['duration']<=0:raise ValueError('Invalid entity label timing or position')
            for l in b['layers']:
                keys=l.get('keyframes')
                if keys is not None:
                    if not l.get('entity_id') or len(keys)<2:raise ValueError('Animated layers need stable entity IDs and at least two keyframes')
                    ats=[k['at'] for k in keys]
                    if ats!=sorted(ats) or ats[0]!=0 or ats[-1]!=1:raise ValueError('Keyframes must run in order from 0 to 1')
                    for k in keys:
                        if not all(math.isfinite(float(k[n])) for n in ('at','x','y','scale','rotation','opacity')) or not 0<=k['opacity']<=1 or k['scale']<=0:raise ValueError('Invalid motion keyframe')
                    prior=entities.get(l['entity_id'])
                    if prior:
                        if prior['svg']!=l['svg']:raise ValueError('A persistent entity must retain its geometry; use a new ID for another object')
                        if any(abs(prior['end'][n]-keys[0][n])>1e-3 for n in ('x','y','scale','rotation','opacity')):raise ValueError('Persistent entity jumps at a beat boundary')
                    entities[l['entity_id']]={'svg':l['svg'],'end':keys[-1]}
                if len(l['svg'])>60000:raise ValueError('SVG layer too large')
                tree=ET.fromstring('<svg>'+l['svg']+'</svg>')
                for el in list(tree.iter())[1:]:
                    if el.tag not in allowed:raise ValueError(f'Disallowed SVG element: {el.tag}')
                    for k,v in el.attrib.items():
                        if k.lower().startswith('on') or k in ('style','src') or (k.endswith('href') and not v.startswith('#')):raise ValueError('Unsafe SVG attribute')
                        if re.search(r'(?:https?:|javascript:|data:|file:)',v,re.I):raise ValueError('External SVG resource not allowed')
                        if 'url(' in v and not re.fullmatch(r'url\(#[A-Za-z0-9_-]+\)',v):raise ValueError('Only local SVG fragment URLs are allowed')
                if not all(math.isfinite(float(l[k])) for k in ('x','y','delay')):raise ValueError('Non-finite visual position')
            count+=1
    return count

async def synthesize(job,script):
    if any(s.get('voice_direction') or s.get('voice_segments') for s in script['scenes']):
        from .voice import synthesize_directed
        return await synthesize_directed(job,script)
    folder=job/'project/public/voice';folder.mkdir(parents=True,exist_ok=True)
    sem=asyncio.Semaphore(4)
    async def one(s):
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}',s['id']):raise ValueError('Unsafe scene ID')
        f=folder/(s['id']+'.json');mp3=folder/(s['id']+'.mp3')
        key=hashlib.sha256(('en-US-GuyNeural|'+s['narration']).encode()).hexdigest()
        if f.exists() and mp3.exists() and read_json(f).get('key')==key:return read_json(f)
        async with sem:
            for attempt in range(3):
                try:
                    words=[];temp=mp3.with_suffix('.pending.mp3')
                    with temp.open('wb') as out:
                        async for chunk in edge_tts.Communicate(s['narration'],'en-US-GuyNeural',boundary='WordBoundary').stream():
                            if chunk['type']=='audio':out.write(chunk['data'])
                            elif chunk['type']=='WordBoundary':words.append({'text':chunk['text'],'start':chunk['offset']/1e7,'end':(chunk['offset']+chunk['duration'])/1e7})
                    dur=float(probe(temp)['format']['duration'])
                    if not words or dur<1:raise ValueError('Missing synthesized speech')
                    temp.replace(mp3);r={'key':key,'file':'voice/'+mp3.name,'seconds':dur,'words':words};write_json(f,r);return r
                except Exception:
                    if attempt==2:raise
                    await asyncio.sleep(2*(attempt+1))
    return await asyncio.gather(*(one(s) for s in script['scenes']))

def build_project(job,script,visuals,voices):
    project=job/'project';public=project/'public';src=project/'src';src.mkdir(parents=True,exist_ok=True)
    engine=ROOT/'remake_engine'
    for f in (engine/'src').glob('*'):shutil.copy2(f,src/f.name)
    for name in ('package.json','tsconfig.json'):shutil.copy2(engine/name,project/name)
    modules=project/'node_modules'
    if not modules.exists():
        # Link creation only; never delete/traverse the shared runtime through this junction.
        run(['cmd','/c','mklink','/J',str(modules),str(ROOT/'tools/motion-studio/node_modules')])
    cursor=0;scenes=[];vmap={s['id']:s for s in visuals['scenes']}
    artwork=read_json(job/'artwork.json') if (job/'artwork.json').exists() else {}
    motion_plan=read_json(job/'motion-plan.json') if (job/'motion-plan.json').exists() else {}
    for s,voice in zip(script['scenes'],voices):
        frames=math.ceil((.15+voice['seconds']+.3)*FPS)
        beats=vmap[s['id']]['beats']; boundaries=[0]
        for i,b in enumerate(beats[1:],1):
            desired=(voice['seconds']+.15)*i/len(beats)
            found=[w['start']+.15 for w in voice['words'] if w['text'].lower().strip('.,:;!?')==b.get('cue_word','').lower().strip('.,:;!?')]
            candidate=min(found,key=lambda x:abs(x-desired)) if found else desired
            # Preserve semantic word cues without letting one misplaced cue
            # create a long frozen shot elsewhere in the scene.
            if abs(candidate-desired)>1.0:candidate=desired
            candidate=max(boundaries[-1]/FPS+2.0,min(candidate,(frames/FPS)-(len(beats)-i)*2))
            boundaries.append(round(candidate*FPS))
        boundaries.append(frames)
        resolved=[]
        for i,b in enumerate(beats):
            item={**b,'from':boundaries[i],'frames':boundaries[i+1]-boundaries[i]}
            item['labels']=[{**l,'from':min(l['from'],max(0,item['frames']/FPS-.75)),'duration':min(l['duration'],item['frames']/FPS-min(l['from'],max(0,item['frames']/FPS-.75)))} for l in b.get('labels',[])]
            art=artwork.get(s['id'],{}).get(str(i))
            if art:
                path=(public/art['file']).resolve()
                if not path.is_relative_to(public.resolve()) or not path.is_file():raise ValueError('Artwork must be an existing local public asset')
                item['art']=art
            resolved.append(item)
        extras=motion_plan.get('scenes',{}).get(s['id'],{})
        for media in extras.get('media',[]):
            path=(public/media['file']).resolve()
            if not path.is_relative_to(public.resolve()) or not path.is_file():raise ValueError('Media must be an existing local public asset')
            if media['type'] not in ('video','image') or media['from']<0 or media['duration']<=0 or media['from']+media['duration']>frames/FPS+.05:raise ValueError('Invalid source-media timing')
        scenes.append({**s,'from':cursor,'frames':frames,'voice':voice['file'],'voiceLead':round(.15*FPS),'words':voice['words'],'beats':resolved,**extras})
        cursor+=frames
    manifest={'title':script['title'],'fps':FPS,'width':1920,'height':1080,'frames':cursor,'scenes':scenes,'subtitles':False,'onScreenText':True,'textPolicy':'section-titles-and-entity-labels-only','textCards':False}
    write_json(src/'manifest.json',manifest);write_json(job/'deliverables/manifest.json',manifest)
    # PCM concatenation on exact frame grid, no speech truncation.
    pcm=job/'narration.wav'
    with wave.open(str(pcm),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
        for s in scenes:
            raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(public/s['voice']),'-f','s16le','-ac','1','-ar',str(SR),'pipe:1'])
            data=b'\0'*(round(s['voiceLead']/FPS*SR)*2)+raw
            total=round(s['frames']/FPS*SR)*2
            if len(data)>total:raise ValueError('Narration would be truncated')
            w.writeframes(data+b'\0'*(total-len(data)))
    return manifest

def sound(job,manifest):
    py=ROOT/'.tools/omnivoice-env/Scripts/python.exe'
    run([py,ROOT/'remake_studio/sound.py',job],timeout=240,log=job/'sound.log')

def render(job):
    project=job/'project'
    cli=ROOT/'tools/motion-studio/node_modules/@remotion/cli/remotion-cli.js'
    output=job/'deliverables/final.pending.mp4'
    concurrency=max(1,min(4,(os.cpu_count() or 2)//2))
    run(['node',cli,'render','src/index.tsx','Remake',output,'--codec=h264','--crf=20',f'--concurrency={concurrency}','--log=error'],cwd=project,timeout=7200,log=job/'render.log')
    data=mux_audio(job,output)
    output.unlink(missing_ok=True)
    run([ROOT/'.tools/omnivoice-env/Scripts/python.exe',ROOT/'remake_studio/verify_render.py',job],timeout=300,log=job/'export-check.log')
    return data

def mux_audio(job,video):
    """Use FFmpeg's gapless decoder: browser MP3 decoding can retain 46ms padding."""
    manifest=read_json(job/'deliverables/manifest.json')
    output=job/'deliverables/final.muxed.mp4'
    run(['ffmpeg','-y','-v','error','-i',video,'-i',job/'deliverables/full-mix.mp3','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',str(manifest['frames']/manifest['fps']),'-movflags','+faststart',output],timeout=300,log=job/'mux.log')
    data=probe(output)
    if not any(s['codec_type']=='audio' for s in data['streams']):raise RuntimeError('Rendered video has no audio')
    output.replace(job/'deliverables/final.mp4')
    return data
