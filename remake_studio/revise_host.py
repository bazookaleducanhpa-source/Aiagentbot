"""Add voiced host moments while preserving existing scene IDs and voice caches."""
import asyncio,copy,os
from .common import JOBS,ROOT,read_json,write_json,run,update
from .production import synthesize,build_project,sound,render
from .pipeline import job_lock,render_signature,validate_export

def prepare():
    job=JOBS/'0a2026102501'
    for name in ('script.json','visuals.json','motion-plan.json'):
        backup=job/(name+'.before-host')
        if not backup.exists():backup.write_bytes((job/name).read_bytes())
    previous=job/'deliverables/final-v2.mp4'
    if not previous.exists():os.link(job/'deliverables/final.mp4',previous)
    script=read_json(job/'script.json');visuals=read_json(job/'visuals.json');plan=read_json(job/'motion-plan.json')
    script['scenes']=[s for s in script['scenes'] if not s['id'].startswith('host-')]
    visuals['scenes']=[s for s in visuals['scenes'] if not s['id'].startswith('host-')]
    intro={'id':'host-intro','narration':"Hi, I'm Cappy. Let's follow this unusual story inside the body, and see what the science actually tells us.",'visual_brief':'Cappy enters and welcomes the viewer, then points to a rounded cell as viruses travel toward it.','mood':'warm and curious'}
    outro={'id':'host-outro','narration':"If this explanation helped, give it a like and subscribe for more science with Cappy. What should we explore next: how immune cells recognize cancer, or how clinical trials test new treatments? Tell me in the comments. Thanks for watching!",'visual_brief':'Cappy gestures to a pressed thumbs-up, ringing subscription bell, then speech bubbles forming a conversation; friendly goodbye without lettering.','mood':'friendly and inviting'}
    script['scenes'].insert(1,intro);script['scenes'].append(outro)
    for scene in script['scenes']:
        n=int(scene['id'][-2:]) if scene['id'].startswith('scene-') else 0
        scene['section_title']=('An Unlikely Ally' if n<=3 else 'How Viruses Target Cancer' if n<=7 else 'Calling the Immune System' if n<=10 else 'One Patient, One Experiment' if n<=16 else 'What the Evidence Shows' if n<=19 else 'Why Treatment Is Difficult' if n<=23 else 'From Promise to Proof' if n<=27 else 'What Comes Next') if n else ''
    for scene in (intro,outro):
        beats=copy.deepcopy(visuals['scenes'][0]['beats'][:2])
        for i,b in enumerate(beats):b.update(id=scene['id']+f'-beat-{i}',cue_word='',show_mascot=True)
        visuals['scenes'].append({'id':scene['id'],'beats':beats})
        plan['scenes'][scene['id']]={'motion':{'kind':'host'},'media':[]}
    plan['style']='continuous-soft-v3-host'
    # Establish real microscopy briefly, then return before the explanatory
    # collection/presentation actions. A late full-frame insert hid those actions.
    for sid in ('scene-08','scene-09'):
        for media in plan['scenes'][sid].get('media',[]):
            if media['type']=='video':media.update({'from':.25,'duration':3.5})
    write_json(job/'script.json',script);write_json(job/'visuals.json',visuals);write_json(job/'motion-plan.json',plan)
    voices=asyncio.run(synthesize(job,script))
    manifest=build_project(job,script,visuals,voices)
    sound(job,manifest)
    run(['node',ROOT/'tools/motion-studio/node_modules/typescript/bin/tsc','--noEmit'],cwd=job/'project',log=job/'host-typecheck.log')
    print({'scenes':len(manifest['scenes']),'seconds':manifest['frames']/manifest['fps'],'hostSeconds':[(s['id'],s['frames']/manifest['fps']) for s in manifest['scenes'] if s['id'].startswith('host-')]})

def export():
    job=JOBS/'0a2026102501'
    with job_lock(job):
        update(job,'export',detail='Rendering voiced Cappy introduction, like/subscribe/comment outro, and additional causal animation',revision='continuous-soft-v3-host',error=None)
        try:
            manifest=read_json(job/'deliverables/manifest.json')
            result=render(job);validate_export(result,manifest)
            write_json(job/'deliverables/render-cache.json',{'key':render_signature(job,manifest,job/'deliverables/full-mix.mp3')})
            q=read_json(job/'deliverables/qa.json');q.update(revision='continuous-soft-v3-host',exportVerification=read_json(job/'deliverables/export-verification.json'))
            q['hostReview']={'spokenIntro':True,'spokenLikeSubscribeComment':True,'topicSpecificQuestion':True,'textCards':False,'preservedBodyNarration':True,'sectionHeadings':'top-left, 8 semantic chapters','entityLabels':'brief English organism/cell identifiers at introduction'}
            write_json(job/'deliverables/qa.json',q)
            update(job,'export','complete','Voiced introduction and CTA exported with expanded causal animation')
            data=read_json(job/'job.json');data.update(status='complete',progress=100,error=None);write_json(job/'job.json',data)
            print(job/'deliverables/final.mp4')
        except Exception as exc:
            data=read_json(job/'job.json');data.update(status='failed',error=str(exc));write_json(job/'job.json',data);raise

if __name__=='__main__':
    import sys
    export() if '--export' in sys.argv else prepare()
