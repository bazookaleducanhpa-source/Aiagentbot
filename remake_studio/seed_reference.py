"""Import the independently researched first production into the local job queue."""
from datetime import datetime,timezone
from .common import ROOT,JOBS,STAGES,write_json,read_json

def seed():
    research=ROOT/'output/remake-0NY2gAftzJE/research'
    analysis=read_json(research/'source-analysis.json'); raw=read_json(research/'suggested-script.json')
    job=JOBS/'0a2026102501';job.mkdir(exist_ok=True)
    source=analysis['source']
    write_json(job/'source/source.json',dict(id=source['id'],url=source['url'],title=source['title'],duration=source['durationSeconds'],channel=source['channel'],description='',transcript=(research/'source.en.txt').read_text(encoding='utf-8'),thumbnail=''))
    report={'summary':analysis['inspection']['originalStructure']+' '+analysis['remake']['approach'],'claims':[{'claim':c['claim'],'assessment':c['status'],'source_url':analysis['references'][0]['url']} for c in analysis['claimLedger']],'risks':['Do not imply viruses alone cured the cancer. Surgery and trastuzumab followed. No actionable self-treatment instructions.'],'improvements':[analysis['remake']['approach']]}
    script={'title':raw['title'],'summary':'An original evidence-aware explanation of oncolytic viruses, one unusual case, and the gap between a promising observation and a proven treatment.','scenes':[{'id':s['id'],'narration':s['narration'],'visual_brief':' | '.join(b['description']+' ('+b['camera']+')' for b in s['visuals']),'mood':'warm scientific curiosity'} for s in raw['scenes']]}
    provenance={'agent':'/root/source_research','source':str(research/'source-analysis.json'),'method':'Independent source viewing, captions, primary case report research and original script.'}
    write_json(job/'approved-research.json',{'artifact':report,'provenance':provenance})
    write_json(job/'approved-script.json',{'artifact':script,'provenance':provenance})
    if not (job/'job.json').exists():write_json(job/'job.json',{'id':job.name,'url':source['url'],'title':script['title'],'status':'interrupted','stage':'source','progress':0,'created_at':datetime.now(timezone.utc).isoformat(),'error':None,'language':'en','notes':'Original visually rich remake. English, no text or subtitles, 90 visual beats, cheerful existing music, white capybara.','stages':[{'id':k,'label':v,'status':'pending','detail':''} for k,v in STAGES]})
    print(job)
if __name__=='__main__':seed()
