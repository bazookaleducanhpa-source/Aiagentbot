"""Measured phrase-level Edge TTS prosody; no unsupported emotion SSML."""
import asyncio
import hashlib
import json
import math
import re
import wave
from pathlib import Path

import edge_tts
from .common import run, read_json, write_json

VOICE = 'en-US-GuyNeural'
SR = 24000
PROFILES = {
    # Keep connected sentences in one request so the voice can carry intonation
    # across the paragraph. Repeated sentence synthesis resets that contour.
    'conversational': ('+1%', '+0Hz', 0),
    'neutral': ('+0%', '+0Hz', 0),
    'engaging': ('-2%', '+2Hz', .18),
    'explanatory': ('-5%', '+0Hz', .22),
    'emphasis': ('-8%', '+3Hz', .3),
    'curious': ('-3%', '+4Hz', .2),
    'warm': ('-3%', '+1Hz', .18),
}

def tokens(text):
    return re.findall(r"\w+(?:['’]\w+)*", text.casefold())

def directed_segments(scene):
    explicit = scene.get('voice_segments')
    if explicit is not None:
        if not isinstance(explicit, list) or not explicit:
            raise ValueError('voice_segments must be a nonempty list')
        segments = [{**s} for s in explicit]
        if tokens(' '.join(s['text'] for s in segments)) != tokens(scene['narration']):
            raise ValueError('voice_segments must preserve every narration word in order')
    else:
        direction = scene.get('voice_direction', 'neutral')
        profile = direction.get('profile', 'neutral') if isinstance(direction, dict) else direction
        if profile not in PROFILES:
            raise ValueError(f'Unknown voice profile: {profile}')
        rate, pitch, pause = PROFILES[profile]
        phrases = [scene['narration']] if profile in {'neutral', 'conversational'} else re.split(r'(?<=[.!?])\s+', scene['narration'].strip())
        segments = [{'text':p,'rate':rate,'pitch':pitch,'pause_after':pause if i<len(phrases)-1 else 0} for i,p in enumerate(phrases) if p.strip()]
    for s in segments:
        s.setdefault('rate', '+0%'); s.setdefault('pitch', '+0Hz'); s.setdefault('pause_after', 0)
        if not s['text'].strip(): raise ValueError('Empty voice segment')
        for field, unit, limit in [('rate','%',30), ('pitch','Hz',30)]:
            if not isinstance(s[field], str) or not re.fullmatch(r'[+-]\d+'+unit, s[field]):
                raise ValueError(f'Invalid {field}: expected signed integer {unit}')
            if abs(int(s[field][:-len(unit)]))>limit: raise ValueError(f'{field} outside subtle prosody range')
        pause=float(s['pause_after'])
        if not math.isfinite(pause) or not 0<=pause<=3: raise ValueError('pause_after must be 0–3 seconds')
        s['pause_after']=pause
    return segments

def cache_key(segments):
    return hashlib.sha256(json.dumps({'version':1,'voice':VOICE,'sr':SR,'segments':segments},sort_keys=True).encode()).hexdigest()

async def synthesize_directed(job, script):
    folder=Path(job)/'project/public/voice'; folder.mkdir(parents=True,exist_ok=True)
    cache=folder/'segments'; cache.mkdir(exist_ok=True)
    sem=asyncio.Semaphore(4)

    inflight={}
    async def segment(s):
        key=cache_key([s])
        if key not in inflight: inflight[key]=asyncio.create_task(generate_segment(s))
        return await inflight[key]

    async def generate_segment(s):
        key=cache_key([s]); wav=cache/(key+'.wav'); meta=cache/(key+'.json')
        if wav.exists() and meta.exists(): return wav,read_json(meta)
        async with sem:
            # Another scene can have generated this identical segment while waiting.
            if wav.exists() and meta.exists(): return wav,read_json(meta)
            for attempt in range(3):
                try:
                    audio=cache/(key+'.pending.mp3'); words=[]
                    with audio.open('wb') as out:
                        async for c in edge_tts.Communicate(s['text'],VOICE,rate=s['rate'],pitch=s['pitch'],boundary='WordBoundary').stream():
                            if c['type']=='audio':out.write(c['data'])
                            elif c['type']=='WordBoundary':words.append({'text':c['text'],'start':c['offset']/1e7,'end':(c['offset']+c['duration'])/1e7})
                    await asyncio.to_thread(run,['ffmpeg','-y','-v','error','-i',audio,'-ac','1','-ar',str(SR),'-c:a','pcm_s16le',wav])
                    with wave.open(str(wav),'rb') as w: samples=w.getnframes()
                    if not words or samples<=0:raise ValueError('Missing synthesized speech')
                    info={'samples':samples,'seconds':samples/SR,'words':words}
                    write_json(meta,info); audio.unlink(missing_ok=True)
                    return wav,info
                except Exception:
                    if attempt==2:raise
                    await asyncio.sleep(2*(attempt+1))

    async def scene(s):
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}',s['id']):raise ValueError('Unsafe scene ID')
        parts=directed_segments(s); key=cache_key(parts)
        mp3=folder/(s['id']+'.mp3'); meta=folder/(s['id']+'.json')
        if mp3.exists() and meta.exists() and read_json(meta).get('key')==key:return read_json(meta)
        words=[]; cursor=0; pcm=bytearray(); measurements=[]
        for part in parts:
            wav,info=await segment(part)
            with wave.open(str(wav),'rb') as w: raw=w.readframes(w.getnframes())
            count=len(raw)//2
            words.extend({**word,'start':word['start']+cursor/SR,'end':word['end']+cursor/SR} for word in info['words'])
            pause=round(part['pause_after']*SR)
            measurements.append({'start_sample':cursor,'speech_samples':count,'pause_samples':pause,'rate':part['rate'],'pitch':part['pitch']})
            pcm.extend(raw); pcm.extend(b'\0'*(pause*2)); cursor+=count+pause
        wav=folder/(s['id']+'.wav')
        with wave.open(str(wav),'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm)
        pending=mp3.with_suffix('.pending.mp3')
        await asyncio.to_thread(run,['ffmpeg','-y','-v','error','-i',wav,'-c:a','libmp3lame','-b:a','128k',pending])
        pending.replace(mp3)
        result={'key':key,'file':'voice/'+mp3.name,'seconds':cursor/SR,'words':words,'sample_rate':SR,'samples':cursor,'segments':measurements}
        write_json(meta,result);return result
    return await asyncio.gather(*(scene(s) for s in script['scenes']))
