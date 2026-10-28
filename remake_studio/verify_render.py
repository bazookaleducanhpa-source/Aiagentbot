"""Verify the encoded deliverable and extract actual video frames for review."""
from pathlib import Path
import json,subprocess,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
FFMPEG=str(next((ROOT/'.tools/ffmpeg').glob('**/bin/ffmpeg.exe')))

def pcm(path):
    p=subprocess.run([FFMPEG,'-v','error','-i',str(path),'-vn','-f','f32le','-ar','16000','-ac','1','pipe:1'],capture_output=True,check=True)
    return np.frombuffer(p.stdout,dtype='<f4')

def verify(job):
    job=Path(job);out=job/'deliverables';manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
    fps=manifest['fps'];movie=out/'final.mp4'
    reference=pcm(out/'full-mix.mp3');actual=pcm(movie)
    length=min(len(reference),len(actual));a=reference[:length:8];b=actual[:length:8]
    correlation=float(np.corrcoef(a,b)[0,1])
    if correlation<.97:raise ValueError(f'Exported soundtrack differs from canonical mix: correlation {correlation}')
    picks=[s['from']+min(45,s['frames']//2) for s in manifest['scenes']]
    select='+'.join(f'eq(n,{n})' for n in picks)
    rows=(len(picks)+5)//6
    subprocess.run([FFMPEG,'-y','-v','error','-i',str(movie),'-vf',f"select='{select}',scale=320:180,tile=6x{rows}",'-frames:v','1',str(out/'contact-sheet.jpg')],check=True)
    subprocess.run([FFMPEG,'-y','-v','error','-ss',str((manifest['frames']-75)/fps),'-i',str(movie),'-frames:v','1',str(out/'ending.png')],check=True)
    report={'audioCorrelationToCanonicalMix':correlation,'decodedDurationSeconds':len(actual)/16000,'expectedDurationSeconds':manifest['frames']/fps,'sampledSceneFrames':len(picks),'contactSheet':'contact-sheet.jpg','ending':'ending.png','passed':True}
    (out/'export-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))
if __name__=='__main__':verify(sys.argv[1])
