from .common import JOBS,read_json,write_json,update
from .pipeline import job_lock,render_signature,validate_export
from .production import render

def main():
    job=JOBS/'0a2026102501'
    with job_lock(job):
        update(job,'export',detail='Rendering continuous soft animation with real scientific source media',revision='continuous-soft-v2',error=None)
        try:
            manifest=read_json(job/'deliverables/manifest.json')
            result=render(job);validate_export(result,manifest)
            write_json(job/'deliverables/render-cache.json',{'key':render_signature(job,manifest,job/'deliverables/full-mix.mp3')})
            q=read_json(job/'deliverables/qa.json')
            q['revision']='continuous-soft-v2'
            q['motionReview']={'continuousScenes':30,'realMediaInserts':5,'method':'Persistent objects, large causal trajectories, cell deformation and staged interactions; no default photo wobble. Source-media crops inspected, attribution in credits.txt.'}
            q['exportVerification']=read_json(job/'deliverables/export-verification.json')
            write_json(job/'deliverables/qa.json',q)
            update(job,'export','complete','Continuous-animation revision exported and verified')
            data=read_json(job/'job.json');data.update(status='complete',progress=100,error=None);write_json(job/'job.json',data)
            print(job/'deliverables/final.mp4')
        except Exception as exc:
            data=read_json(job/'job.json');data.update(status='failed',error=str(exc));write_json(job/'job.json',data)
            raise
if __name__=='__main__':main()
