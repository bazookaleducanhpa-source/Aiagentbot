"""Package verified video with an explicitly supplied, reviewed thumbnail."""
from pathlib import Path
import shutil
from .common import read_json,write_json,run,probe

def package_delivery(job,destination,thumbnail,title=None,alternatives=None):
    job=Path(job);destination=Path(destination);thumbnail=Path(thumbnail)
    video=job/'deliverables/final.mp4'
    for path in (video,thumbnail):
        if not path.is_file() or not path.stat().st_size:raise FileNotFoundError(f'Missing delivery asset: {path}')
    script=read_json(job/'script.json');title=(title or script['title']).strip()
    if not title:raise ValueError('Delivery title is empty')
    destination.mkdir(parents=True,exist_ok=True)
    def copy(src,name):
        dst=destination/name
        if Path(src).resolve()!=dst.resolve():shutil.copy2(src,dst)
    copy(video,'video.mp4')
    if thumbnail.parent.resolve()!=destination.resolve():copy(thumbnail,'thumbnail-master'+thumbnail.suffix.lower())
    converted=destination/'thumbnail.pending.jpg'
    run(['ffmpeg','-y','-v','error','-i',thumbnail,'-vf','scale=1280:720','-frames:v','1','-q:v','2',converted])
    converted.replace(destination/'thumbnail.jpg')
    (destination/'title.txt').write_text(title+'\n',encoding='utf-8')
    if alternatives:(destination/'title-alternatives.txt').write_text('\n'.join(alternatives)+'\n',encoding='utf-8')
    for name in ('credits.txt','qa.json'):
        if (job/'deliverables'/name).is_file():copy(job/'deliverables'/name,name)
    copy(job/'script.json','script.json')
    shutil.copy2(destination/'thumbnail.jpg',job/'deliverables/thumbnail.jpg')
    shutil.copy2(destination/'title.txt',job/'deliverables/title.txt')
    result={'title':title,'job':job.name,'video':'video.mp4','thumbnail':'thumbnail.jpg','titleFile':'title.txt','status':'complete','durationSeconds':float(probe(destination/'video.mp4')['format']['duration'])}
    write_json(destination/'package.json',result)
    return result
