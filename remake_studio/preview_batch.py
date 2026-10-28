"""Render an isolated illustration proof without touching production output."""
import sys,shutil
from .common import ROOT,JOBS,read_json,run
from .production import build_project

def main():
    job=JOBS/sys.argv[1];batch=sys.argv[2]
    visuals=read_json(job/'agents'/f'visuals-{batch}.json');ids={s['id'] for s in visuals['scenes']}
    script=read_json(job/'script.json');script['scenes']=[s for s in script['scenes'] if s['id'] in ids]
    proof=job/'proof';(proof/'project/public/voice').mkdir(parents=True,exist_ok=True)
    if (job/'artwork.json').exists():
        shutil.copy2(job/'artwork.json',proof/'artwork.json')
        shutil.copytree(job/'project/public/art',proof/'project/public/art',dirs_exist_ok=True)
    voices=[]
    for s in script['scenes']:
        meta=read_json(job/'project/public/voice'/(s['id']+'.json'));voices.append(meta)
        shutil.copy2(job/'project/public'/meta['file'],proof/'project/public'/meta['file'])
    manifest=build_project(proof,script,visuals,voices)
    run(['node',ROOT/'tools/motion-studio/node_modules/typescript/bin/tsc','--noEmit'],cwd=proof/'project',log=proof/'typecheck.log')
    for i,s in enumerate(manifest['scenes']):
        run(['node',ROOT/'tools/motion-studio/node_modules/@remotion/cli/remotion-cli.js','still','src/index.tsx','Remake',proof/f'proof-{i}.png','--frame',str(s['from']+45),'--log=error'],cwd=proof/'project',timeout=300,log=proof/f'still-{i}.log')
    print(proof)
if __name__=='__main__':main()
