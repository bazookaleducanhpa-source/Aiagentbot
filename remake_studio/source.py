import json,re,sys,urllib.parse
from pathlib import Path
from .common import run,write_json,read_json,ROOT

def video_id(url):
    try:u=urllib.parse.urlsplit(url)
    except ValueError:raise ValueError('Link YouTube không hợp lệ')
    if u.scheme not in ('https','http') or u.username or u.password:raise ValueError('Chỉ nhận link YouTube công khai')
    host=(u.hostname or '').lower()
    if host=='youtu.be':value=u.path.strip('/').split('/')[0]
    elif host in ('youtube.com','www.youtube.com','m.youtube.com'):
        if u.path=='/watch':value=urllib.parse.parse_qs(u.query).get('v',[''])[0]
        elif u.path.startswith(('/shorts/','/embed/')):value=u.path.split('/')[2]
        else:value=''
    else:raise ValueError('Chỉ nhận youtube.com hoặc youtu.be')
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}',value):raise ValueError('Không tìm thấy video ID hợp lệ')
    return value

def parse_vtt(text):
    lines=[]; previous=''
    for line in text.splitlines():
        if not line.strip() or '-->' in line or line.startswith(('WEBVTT','Kind:','Language:')) or line.strip().isdigit():continue
        line=re.sub(r'<[^>]+>','',line).strip()
        if line and line!=previous:lines.append(line);previous=line
    return '\n'.join(lines)

def acquire(job,url):
    folder=job/'source';folder.mkdir(exist_ok=True)
    if (folder/'source.json').exists():return read_json(folder/'source.json')
    vid=video_id(url); canonical='https://www.youtube.com/watch?v='+vid
    try:
        run([sys.executable,'-m','yt_dlp','--no-playlist','--skip-download','--write-info-json','--write-subs','--write-auto-subs','--sub-langs','en,en-orig,vi','--sub-format','vtt','-o',str(folder/'reference.%(ext)s'),canonical],timeout=240,log=folder/'download.log')
    except RuntimeError:
        # Caption rate limits must not discard successfully fetched metadata.
        if not (folder/'reference.info.json').exists():
            run([sys.executable,'-m','yt_dlp','--no-playlist','--skip-download','--write-info-json','-o',str(folder/'reference.%(ext)s'),canonical],timeout=180,log=folder/'metadata.log')
    info=read_json(folder/'reference.info.json')
    candidates=list(folder.glob('reference.en*.vtt'))+list(folder.glob('reference.vi*.vtt'))
    transcript=parse_vtt(candidates[0].read_text(encoding='utf-8')) if candidates else ''
    if not transcript:
        run([sys.executable,'-m','yt_dlp','--no-playlist','-f','bestaudio','-o',str(folder/'reference-audio.%(ext)s'),canonical],timeout=600,log=folder/'audio-download.log')
        audio=next(p for p in folder.glob('reference-audio.*') if p.suffix not in ('.part','.ytdl'))
        helper=ROOT/'remake_studio/transcribe.py';py=ROOT/'.tools/audio-align-env/Scripts/python.exe'
        run([py,helper,audio,folder/'transcript.txt'],timeout=1200,log=folder/'transcribe.log')
        transcript=(folder/'transcript.txt').read_text(encoding='utf-8')
    if len(transcript)<100:raise RuntimeError('Không lấy được nội dung video đủ để remake; cần phụ đề hoặc audio đọc được.')
    data={'id':vid,'url':canonical,'title':info.get('title',vid),'duration':info.get('duration'),'channel':info.get('channel'),'description':info.get('description','')[:12000],'transcript':transcript,'thumbnail':info.get('thumbnail')}
    # Inspect actual source imagery as well as its transcript. Reference footage
    # remains separate from final assets and is never silently reused.
    try:
        run([sys.executable,'-m','yt_dlp','--no-playlist','-f','best[height<=480]/bestvideo[height<=480]','-o',str(folder/'reference-video.%(ext)s'),canonical],timeout=600,log=folder/'video-download.log')
        video=next(p for p in folder.glob('reference-video.*') if p.suffix not in ('.part','.ytdl'))
        step=max(1,float(info.get('duration') or 300)/24)
        run(['ffmpeg','-y','-v','error','-i',video,'-vf',f'fps=1/{step},scale=320:-1,tile=5x5','-frames:v','1',folder/'contact-sheet.jpg'],timeout=180)
        data['visual_inspection']='25 sampled source frames supplied to research agent; not frame-by-frame viewing.'
    except Exception as e:
        data['visual_inspection']='Source frame sampling unavailable; transcript-only analysis: '+str(e)[:250]
    write_json(folder/'source.json',data)
    return data
