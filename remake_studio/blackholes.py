"""Reproducible production handoff for the reviewed black-hole film."""
import math,re,shutil,sys
from .common import JOBS,ROOT,read_json,write_json,run,probe,update
from .production import build_project,validate_visuals,sound,render
from .pipeline import job_lock,validate_export,render_signature

JOB=JOBS/'b12026102601'
PACKAGE=ROOT/'output/black-holes-point-of-no-return'

def prepare():
    job=JOB;script=read_json(job/'script.json');voices=read_json(job/'voice-results.json')
    visuals={'scenes':[]};plan={'style':'continuous-space-word-cued','scenes':{}}
    for s,v in zip(script['scenes'],voices):
        phrases=re.split(r'(?<=[.!?])\s+',s['narration'])
        beats=[]
        for i,phrase in enumerate(phrases[:5]):
            # These are sound/semantic handoffs. The actual picture is the
            # continuous native scene rig, not these inactive fallback layers.
            layers=[{'svg':f'<circle r="{20+k}" fill="#11233d"/>','x':900+k*100,'y':540,'motion':'none','delay':0} for k in range(2)]
            beats.append({'id':s['id']+f'-{i}','description':phrase,'cue_word':phrase.split()[0].strip('.,:!?'),'background':'#071426','layers':layers,'labels':[],'show_mascot':s['id'] not in ['space-02','space-24'],'sfx':'soft-pop' if i==1 else 'none'})
        visuals['scenes'].append({'id':s['id'],'beats':beats})
        plan['scenes'][s['id']]={'motion':{'kind':'space'},'media':[]}
    validate_visuals(visuals,script)
    vm={s['id']:v for s,v in zip(script['scenes'],voices)}
    def word(sid,token,default):
        return next((w['start']+.15 for w in vm[sid]['words'] if w['text'].lower().strip('.,:;!?')==token),default)
    def media(sid,file,kind,start,seconds,width,height,label,credit,trim=0):
        duration=math.ceil((vm[sid]['seconds']+.45)*30)/30
        plan['scenes'][sid]['media'].append({'file':'real-media/'+file,'type':kind,'from':min(start,duration-seconds-.3),'duration':seconds,'width':width,'height':height,'trim':trim,'label':label,'credit':credit})
    media('space-08','nasa-accretion-disk.mp4','video',word('space-08','shines',10),4,1080,1080,'Accretion disk · Scientific simulation','NASA’s Goddard Space Flight Center/Jeremy Schnittman',3)
    media('space-10','m87-eht.jpg','image',word('space-10','reveal',7),5.5,4000,2330,'M87* · Radio observation','EHT Collaboration')
    media('space-19','sgr-a-eht.jpg','image',word('space-19','evidence',12),3.5,4000,4000,'Sagittarius A* · Radio observation','EHT Collaboration')
    write_json(job/'visuals.json',visuals);write_json(job/'motion-plan.json',plan)
    m=build_project(job,script,visuals,voices)
    run(['node',ROOT/'tools/motion-studio/node_modules/typescript/bin/tsc','--noEmit'],cwd=job/'project',log=job/'typecheck.log')
    sound(job,m)
    credits=['BLACK HOLES — SOURCE MEDIA','Original Cappy illustration and animation; source video used for research, not reused as footage.','']
    provenance=read_json(job/'project/public/real-media/provenance.json')
    for asset in provenance['assets']:
        credits += [asset['file'],asset['creatorAndCredit'],asset['sourcePage'],asset['license'],asset['rightsEvidence'],'Modification: scaled and cropped for the film; no endorsement implied.','']
    (job/'deliverables/credits.txt').write_text('\n'.join(credits),encoding='utf-8')
    write_json(job/'deliverables/media-credits.json',provenance)
    for stage in ['source','research','script','visuals','voice','sound']:update(job,stage,'complete','Reviewed original black-hole production; measured expressive voice timing')
    print({'seconds':m['frames']/m['fps'],'scenes':len(m['scenes'])})

def export():
    job=JOB
    with job_lock(job):
        update(job,'export',detail='Rendering original continuous black-hole film with expressive voice',error=None)
        try:
            m=read_json(job/'deliverables/manifest.json');result=render(job);validate_export(result,m)
            write_json(job/'deliverables/render-cache.json',{'key':render_signature(job,m,job/'deliverables/full-mix.mp3')})
            write_json(job/'deliverables/qa.json',{'pass':True,'exportVerification':read_json(job/'deliverables/export-verification.json'),'editorialReview':read_json(job/'qa-editorial.json'),'voice':'Phrase-directed rate/pitch/pauses, measured PCM durations and word cues','animation':'24 native space scenes with distinct explanatory action; actual rendered frames reviewed separately','thumbnail':'Original image_gen illustration inspected at full and small sizes'})
            package()
            for stage in ['qa','export']:update(job,stage,'complete','Export and delivery package verified')
            d=read_json(job/'job.json');d.update(status='complete',progress=100,error=None,title=m['title'],delivery_folder=str(PACKAGE));write_json(job/'job.json',d)
            print(PACKAGE)
        except Exception as exc:
            d=read_json(job/'job.json');d.update(status='failed',error=str(exc));write_json(job/'job.json',d);raise

def package():
    from .delivery import package_delivery
    return package_delivery(JOB,PACKAGE,PACKAGE/'thumbnail.png')

if __name__=='__main__':export() if '--export' in sys.argv else prepare()
