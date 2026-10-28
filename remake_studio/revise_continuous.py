"""Apply the reviewed continuous-animation direction to the first production."""
import os,shutil
from .common import JOBS,ROOT,read_json,write_json,run
from .production import build_project

def prepare():
    job=JOBS/'0a2026102501';old=job/'deliverables/final.mp4';backup=job/'deliverables/final-v1.mp4'
    if old.exists() and not backup.exists():os.link(old,backup)
    script=read_json(job/'script.json');visuals=read_json(job/'visuals.json')
    voices=[read_json(job/'project/public/voice'/(s['id']+'.json')) for s in script['scenes']]
    previous=read_json(job/'deliverables/manifest.json');dur={s['id']:s['frames']/previous['fps'] for s in previous['scenes']}
    bio={1,3,4,5,6,7,8,9,10,14,20,21,22,28}
    plan={'style':'continuous-soft-v2','scenes':{s['id']:{'motion':{'kind':'biology' if int(s['id'][-2:]) in bio else 'story'},'media':[]} for s in script['scenes']}}
    def media(s,file,kind,seconds,width,height,crop=None,trim=0):
        item={'file':'real-media/'+file,'type':kind,'from':dur[s]-seconds-.25,'duration':seconds,'width':width,'height':height,'trim':trim}
        if crop:item['crop']=crop
        plan['scenes'][s]['media'].append(item)
    media('scene-08','tcell-video1.mp4','video',6,1278,700,[290,85,680,510],8)
    media('scene-09','tcell-video3.mp4','video',6,722,720,[0,0,722,640],1)
    media('scene-13','halassy-paper-figure2.png','image',4,2182,1242,[175,820,348,155])
    media('scene-14','halassy-paper-figure2.png','image',4,2182,1242,[760,496,618,210])
    media('scene-28','nih-tcells-cancer.jpg','image',3.5,601,401)
    write_json(job/'motion-plan.json',plan)
    manifest=build_project(job,script,visuals,voices)
    run(['node',ROOT/'tools/motion-studio/node_modules/typescript/bin/tsc','--noEmit'],cwd=job/'project',log=job/'continuous-typecheck.log')
    provenance=read_json(job/'project/public/real-media/provenance.json')
    write_json(job/'deliverables/media-credits.json',provenance)
    credits=['SOURCE MEDIA / ATTRIBUTION','Video excerpts and stills are cropped; microscope footage shows laboratory T-cell behavior, not Halassy or her treatment.','']
    for a in provenance['assets']:
        credits += [a.get('credit',a['creator']),a['sourcePage'],a['license']+' — '+a['licenseUrl'],'']
    (job/'deliverables/credits.txt').write_text('\n'.join(credits),encoding='utf-8')
    print({'duration':manifest['frames']/manifest['fps'],'continuousScenes':len(plan['scenes']),'sourceMediaInserts':sum(len(s['media']) for s in plan['scenes'].values())})
if __name__=='__main__':prepare()
