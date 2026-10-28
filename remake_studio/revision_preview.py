"""Extract a concise review of the latest actual encoded revision."""
from .common import JOBS,read_json,run,probe,write_json

def main():
    job=JOBS/'0a2026102501';out=job/'deliverables';m=read_json(out/'manifest.json');fps=m['fps']
    ids=['host-intro','scene-05','scene-13','scene-15','scene-16','host-outro']
    scenes=[next(s for s in m['scenes'] if s['id']==sid) for sid in ids]
    args=['ffmpeg','-y','-v','error'];filters=[];links=[];total=0
    for i,s in enumerate(scenes):
        duration=min(7,s['frames']/fps) if s['id']=='scene-05' else s['frames']/fps
        args+=['-ss',str(s['from']/fps),'-t',str(duration),'-i',out/'final.mp4']
        filters+=[f'[{i}:v]setpts=PTS-STARTPTS[v{i}]',f'[{i}:a]asetpts=PTS-STARTPTS[a{i}]']
        links.append(f'[v{i}][a{i}]');total+=duration
    filters+=[''.join(links)+f'concat=n={len(scenes)}:v=1:a=1[v][a]']
    args+=['-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','libx264','-crf','21','-preset','veryfast','-threads','4','-c:a','aac','-b:a','160k','-movflags','+faststart',out/'revision-preview.mp4']
    run(args,timeout=300,log=job/'revision-preview.log')
    result=probe(out/'revision-preview.mp4');actual=float(result['format']['duration'])
    if abs(actual-total)>.2:raise ValueError('Review preview duration mismatch')
    write_json(out/'revision-preview.json',{'scenes':ids,'seconds':actual,'source':'final.mp4'})
    print({'previewSeconds':actual,'file':str(out/'revision-preview.mp4')})

if __name__=='__main__':main()
