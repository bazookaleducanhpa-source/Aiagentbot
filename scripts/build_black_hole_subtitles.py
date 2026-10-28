"""Build external multilingual SRT files from measured final-film narration."""
import argparse
import json
import re
import math
import unicodedata
import zipfile
import regex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'output/black-holes-point-of-no-return-v2'
OUT = PACKAGE / 'subtitles'
MANIFEST = ROOT / 'data/remake-jobs/b12026102702/deliverables/manifest.json'


def tokens(text):
    return re.findall(r'[a-z0-9]+', text.lower())


def prepare():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    rows=[]
    for scene in manifest['scenes']:
        measured=[]
        for word in scene['words']:
            measured.extend(dict(token=t, start=word['start'], end=word['end']) for t in tokens(word['text']))
        expected=tokens(scene['narration'])
        if expected != [w['token'] for w in measured]:
            raise ValueError('Word/text alignment differs: '+scene['id'])
        offset=(scene['from']+scene['voiceLead'])/manifest['fps']
        cursor=0
        for number,text in enumerate(re.split(r'(?<=[.!?])\s+', scene['narration']),1):
            length=len(tokens(text))
            rows.append(dict(id=f"{scene['id']}-{number:02d}",scene=scene['id'],text=text,
                             startMs=round((offset+measured[cursor]['start'])*1000),
                             endMs=round((offset+measured[cursor+length-1]['end'])*1000)))
            cursor+=length
        assert cursor==len(measured)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'translations').mkdir(exist_ok=True)
    source=dict(title=manifest['title'],description='Explore how black holes form, what an event horizon means, how we observe them, and what physics predicts about their distant future. An illustrated science journey with Cappy.',durationMs=round(manifest['frames']/manifest['fps']*1000),segments=rows)
    (OUT/'source-segments.json').write_text(json.dumps(source,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'translations/en.json').write_text(json.dumps(dict(language='en',title=source['title'],description=source['description'],segments={r['id']:r['text'] for r in rows}),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Prepared',len(rows),'sentence-aligned translation units')


LANGUAGES={'en':'English','vi':'Vietnamese','ko':'Korean','ja':'Japanese','fr':'French','de':'German','ru':'Russian','pt-BR':'Portuguese-Brazil','hi':'Hindi-India'}


def width(text):
    return sum(2 if unicodedata.east_asian_width(g[0]) in {'W','F'} else 1 for g in regex.findall(r'\X',text))


def units(text,lang):
    if lang=='ja':
        # Never split a Latin name or a Unicode grapheme/combining sequence.
        parts=regex.findall(r'[A-Za-z0-9]+(?:[-\x27][A-Za-z0-9]+)*|\X',text)
        result=[]
        for part in parts:
            if part in '、。，．！？!?」』）)]' and result:
                result[-1]+=part
            else:
                result.append(part)
        return result,''
    return text.split(),' '


def chunks(text,lang):
    parts,join=units(text,lang)
    total=width(text)
    count=max(1,math.ceil(total/78))
    result=[]
    while parts:
        target=width(join.join(parts))/count
        take=1
        while take<len(parts):
            before=width(join.join(parts[:take]))
            after=width(join.join(parts[:take+1]))
            if after>84 or abs(before-target)<=abs(after-target):
                break
            take+=1
        result.append(join.join(parts[:take]))
        parts=parts[take:]
        count=max(1,count-1)
    safe=[]
    pending=result[:]
    while pending:
        item=pending.pop(0)
        try:
            lines(item,lang)
            safe.append(item)
        except ValueError:
            bits,sep=units(item,lang)
            if len(bits)<2:
                raise
            split=min(range(1,len(bits)),key=lambda i:abs(width(sep.join(bits[:i]))-width(sep.join(bits[i:]))))
            pending[:0]=[sep.join(bits[:split]),sep.join(bits[split:])]
    return safe


def lines(text,lang):
    if width(text)<=42:
        return text
    parts,join=units(text,lang)
    choices=[]
    for i in range(1,len(parts)):
        a,b=join.join(parts[:i]),join.join(parts[i:])
        if max(width(a),width(b))<=42:
            choices.append((abs(width(a)-width(b)),a,b))
    if not choices:
        raise ValueError(f'Cannot wrap two lines: {lang}: {text}')
    _,a,b=min(choices)
    return a+'\n'+b


def stamp(ms):
    seconds,milli=divmod(ms,1000)
    minutes,second=divmod(seconds,60)
    hour,minute=divmod(minutes,60)
    return f'{hour:02d}:{minute:02d}:{second:02d},{milli:03d}'


def build():
    source=json.loads((OUT/'source-segments.json').read_text(encoding='utf-8'))
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    ids={r['id'] for r in source['segments']}
    scene_ends={s['id']:round((s['from']+s['frames'])/manifest['fps']*1000) for s in manifest['scenes']}
    measured={}
    for scene in manifest['scenes']:
        offset=(scene['from']+scene['voiceLead'])/manifest['fps']*1000
        measured[scene['id']]=[dict(token=t,startMs=round(offset+w['start']*1000),endMs=round(offset+w['end']*1000)) for w in scene['words'] for t in tokens(w['text'])]
    reports={}
    metadata={}
    files=[]
    for lang,name in LANGUAGES.items():
        translation=json.loads((OUT/'translations'/f'{lang}.json').read_text(encoding='utf-8'))
        assert set(translation['segments'])==ids,(lang,'missing or extra sentences')
        assert all(isinstance(t,str) and t.strip() and '\ufffd' not in t for t in translation['segments'].values()),lang
        captions=[]
        cursors={scene:0 for scene in measured}
        coverage=[]
        for ri,row in enumerate(source['segments']):
            text=translation['segments'][row['id']].strip()
            groups=chunks(text,lang)
            # Allow a small natural reading tail; never leak into the next sentence/scene.
            following=source['segments'][ri+1]['startMs'] if ri+1<len(source['segments']) else source['durationMs']
            end=min(row['endMs']+350,following-50,scene_ends[row['scene']]-30)
            if lang=='en':
                timing=[]
                for group in groups:
                    cursor=cursors[row['scene']]
                    length=len(tokens(group))
                    words=measured[row['scene']][cursor:cursor+length]
                    assert [w['token'] for w in words]==tokens(group)
                    timing.append((words[0]['startMs'],words[-1]['endMs']))
                    cursors[row['scene']]+=length
            else:
                weights=[width(t) for t in groups]
                starts=[row['startMs']+round((end-row['startMs'])*sum(weights[:i])/sum(weights)) for i in range(len(groups)+1)]
                timing=[(starts[i],starts[i+1]-20 if i<len(groups)-1 else end) for i in range(len(groups))]
            for i,(group,(start,stop)) in enumerate(zip(groups,timing)):
                if lang=='en':
                    stop=min(stop+220,timing[i+1][0]-30 if i+1<len(timing) else end)
                assert 0<=start<stop<=source['durationMs'],(lang,row['id'],start,stop)
                captions.append(dict(text=lines(group,lang),startMs=start,endMs=stop,timestampMs=None,confidence=None))
            coverage.append(row['id'])
        assert len(coverage)==102
        for a,b in zip(captions,captions[1:]):
            assert a['endMs']<=b['startMs'],(lang,'overlap')
        # SRT serialization round-trip check below also verifies UTF-8 and cue numbering.
        path=OUT/f'black-holes.{lang}.srt'
        srt='\n\n'.join(f"{i}\n{stamp(c['startMs'])} --> {stamp(c['endMs'])}\n{c['text']}" for i,c in enumerate(captions,1))+'\n'
        path.write_text(srt,encoding='utf-8',newline='\n')
        blocks=path.read_text(encoding='utf-8').strip().split('\n\n')
        assert len(blocks)==len(captions)
        for i,block in enumerate(blocks,1):
            fields=block.splitlines()
            assert fields[0]==str(i) and re.fullmatch(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}',fields[1])
            assert 1<=len(fields[2:])<=2
            assert all(width(line)<=42 for line in fields[2:])
        if lang=='en':
            assert tokens(' '.join(c['text'] for c in captions))==tokens(' '.join(r['text'] for r in source['segments']))
        (OUT/f'black-holes.{lang}.captions.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2),encoding='utf-8')
        reports[lang]=dict(file=path.name,cues=len(captions),sentences=102,first_ms=captions[0]['startMs'],last_ms=captions[-1]['endMs'],min_cue_ms=min(c['endMs']-c['startMs'] for c in captions),max_lines=2,max_line_display_cells=42,encoding='UTF-8',overlaps=0)
        metadata[lang]=dict(language=name,title=translation['title'],description=translation['description'])
        files.append(path)
    (OUT/'localized-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'localized-titles-and-descriptions.txt').write_text('\n\n'.join(f"[{lang}] {m['language']}\nTITLE: {m['title']}\nDESCRIPTION: {m['description']}" for lang,m in metadata.items())+'\n',encoding='utf-8')
    qa=dict(video='../video.mp4',video_duration_ms=source['durationMs'],english_timing='Measured English word boundaries on final 30fps video timeline, including actual voice lead',translation_timing='Sentence boundaries follow English speech; within-sentence translated cues use proportional text allocation, not translated word-level forced alignment',translation_review='Model translations; no independent native-speaker proofreading claimed',languages=reports)
    (OUT/'subtitle-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    archive=PACKAGE/'black-holes-subtitles-9-languages.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as target:
        for path in files:
            target.write(path,path.name)
    with zipfile.ZipFile(archive) as check:
        assert check.testzip() is None and len(check.namelist())==9
    print(json.dumps(dict(zip=str(archive),files=reports),ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['prepare','build'])
    args=parser.parse_args()
    {'prepare':prepare,'build':build}[args.stage]()
